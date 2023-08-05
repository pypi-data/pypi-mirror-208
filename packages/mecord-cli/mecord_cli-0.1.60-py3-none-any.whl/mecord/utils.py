import uuid
import platform
import subprocess
import qrcode
import qrcode_terminal
import os
import sys
import requests
from io import BytesIO
import psutil
import pynvml
import logging
import datetime
import calendar
import time
import http
import json
import oss2
from pathlib import Path
import zipfile
import re

from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer, CircleModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SquareGradiantColorMask, SolidFillColorMask


CACHE_QRCODE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login_qrcode.png")

def get_mac_from_nettools():
    try:
        cmd = "ifconfig"
        output = subprocess.check_output(cmd, shell=True)
        output_str = output.decode(encoding='UTF-8')
        mac = output_str[output_str.index('ether') + 6:output_str.index('ether') + 23].replace(':', '')
        return True, mac
    except Exception as e:
        return False, None
    
def get_mac_from_system():
    try:
        root_path = '/sys/class/net/'
        dbtype_list = os.listdir(root_path)
        for dbtype in dbtype_list:
            if os.path.isfile(os.path.join(root_path, dbtype)):
                dbtype_list.remove(dbtype)

        if len(dbtype_list) == 0:
            return False, None
        mac = ''
        for dbtype in dbtype_list:
          cmd = f"cat {root_path}{dbtype}/address"
          output = subprocess.check_output(cmd, shell=True)
          mac += output.decode(encoding='UTF-8')
        return True, mac
    except Exception as e:
        return False, None

def get_mac_address():
    if platform.system() == 'Windows':
        cmd = "ipconfig /all"
        output = subprocess.check_output(cmd, shell=True)
        output_str = output.decode('gbk')
        pos = output_str.find('Physical Address')
        if pos == -1:
            pos = output_str.find('物理地址')
        mac = (output_str[pos:pos+100].split(':')[1]).strip().replace('-', '')
    elif platform.system() == 'Linux' or platform.system() == 'Darwin':
        ok, mac = get_mac_from_nettools()
        if ok:
            return mac
        ok, mac = get_mac_from_system()
        if ok:
            return mac
        return None
    else:
        mac = None
    return mac

def get_cpu_serial():
    cpu_serial = ""
    if platform.system() == 'Windows':
        cmd = "wmic cpu get ProcessorId"
        output = subprocess.check_output(cmd, shell=True)
        output_str = output.decode('gbk')
        pos = output_str.index("\n")
        cpu_serial = output_str[pos:].strip()
    elif platform.system() == 'Linux':
        with open('/proc/cpuinfo') as f:
            
            for line in f:
                if line[0:6] == 'Serial':
                    return "1"
                if line.strip().startswith('serial'):
                    cpu_serial = line.split(":")[1].strip()
                    break
        if not cpu_serial:
            cpu_serial = None
    elif platform.system() == 'Darwin':
        cmd = "/usr/sbin/system_profiler SPHardwareDataType"
        output = subprocess.check_output(cmd, shell=True)
        output_str = output.decode(encoding='UTF-8')
        cpu_serial = output_str[output_str.index('Hardware UUID:') + 14:output_str.index('Hardware UUID:') + 51].replace('-', '')
    else:
        cpu_serial = None
    return cpu_serial

#salt with mecord device variable
def get_salt():
    salt = ""
    if "MECORD_DEVICEID_SALT" in os.environ:
        salt = str(os.getenv("MECORD_DEVICEID_SALT"))

    salt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salt.txt")
    salt_file = open(salt_file_path, 'a+')
    salt_file.seek(0, 0)
    line = salt_file.readline()
    if line.startswith('MECORD_DEVICEID_SALT='):
        salt = line[len('MECORD_DEVICEID_SALT='):]

    salt_file.truncate(0)
    line = 'MECORD_DEVICEID_SALT={value}'.format(value=salt)
    salt_file.write(line)
    salt_file.close()
    
    return salt

def generate_unique_id():
    mac = get_mac_address()
    cpu_serial = get_cpu_serial()
    salt = get_salt()
    if mac and cpu_serial:
        unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, mac + cpu_serial + salt)
        return str(unique_id).replace('-', '')
    if mac :
        unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, mac + salt)
        return str(unique_id).replace('-', '')

def displayQrcode(s):
    cache_qrcode_file = create_qrcode(s)
    if platform.system() == 'Windows':
        os.system(f"start {cache_qrcode_file} &")
    elif platform.system() == 'Linux' or platform.system() == 'Darwin':
        qrcode_terminal.draw(s)


def create_qrcode(s):
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(s)
    qr.make(fit=True)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=CircleModuleDrawer(),
        color_mask=SolidFillColorMask(),
        fill_color=(0, 0, 0),
        back_color=(255, 255, 255))

    img.save(CACHE_QRCODE_FILE)
    return CACHE_QRCODE_FILE


def displayQRcodeOnTerminal(s):
    qrcode_terminal.draw(s)

def getOssImageSize(p):
    try:
        s = requests.session()
        s.keep_alive = False
        res = s.get(p)
        image = Image.open(BytesIO(res.content), "r")
        s.close()
        return image.size
    except:
        return 0, 0
    
def deviceInfo():
    M=1024*1024
    data = {
        "cpu": {
            "logical_count" : psutil.cpu_count(),
            "count" : psutil.cpu_count(logical=False),
            "max_freq" : f"{psutil.cpu_freq().max / 1000} GHz",
        },
        "memory": {
            "total" : f"{psutil.virtual_memory().total/M} M",
            "free" : f"{psutil.virtual_memory().free/M} M"
        },
        "gpu": {
            "count" : 0,
            "list" : [],
            "mem" : []
        }
    }
    try:
        pynvml.nvmlInit()
        gpuCount = pynvml.nvmlDeviceGetCount()
        data["gpu"]["count"] = gpuCount
        for i in range(gpuCount):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            data["gpu"]["list"].append(f"GPU{i}: {pynvml.nvmlDeviceGetName(handle)}")
            memInfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
            data["gpu"]["mem"].append(f"GPU{i}: total:{memInfo.total/M} M free:{memInfo.free/M} M")
            
        pynvml.nvmlShutdown()
    except Exception as e:
        data["gpu"]["count"] = 1
        data["gpu"]["list"].append(f"GPU0: Normal")
    return data

class LogStdout(object):
    def __init__(self):
        self.stdout = sys.stdout

    def write(self, message):
        logging.info(message)
        self.stdout.write(message)

    def flush(self):
        self.stdout.flush()

    def __del__(self):
        self.close()

    def close(self):
        sys.stdout = self.stdout

def mecordPrint(s, no_print=False):
    # if no_print == False:
    d = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    print(d + ' ' + s)

def reportLog():
    reason = ""
    if len(sys.argv) >= 2:
        reason = sys.argv[2].strip().replace("\n","").replace(",","").replace(" ","").replace(";","")
    d = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    uid = generate_unique_id()

    thisFileDir = os.path.dirname(os.path.abspath(__file__))
    dist = os.path.join(thisFileDir, f"{uid}_{reason}_{d}.zip")
    zip = zipfile.ZipFile(dist, "w", zipfile.ZIP_DEFLATED) 

    for root,dirs,files in os.walk(thisFileDir):
        for file in files:
            if str(file).startswith("~$"):
                continue
            name = file[0:file.index(".")]
            ext = file[file.index("."):]
            if ext == ".log" or ext == ".json":
                filepath = os.path.join(root, file)
                zip.write(filepath, file)
        if root != files:
            break
    zip.close()
    ossurl = uploadOSS(dist)
    os.remove(dist)
    return ossurl

def uploadOSS(file):
    conn = http.client.HTTPSConnection("api.mecordai.com")
    payload = json.dumps({
        "sign": "f0463f490eb84133c0aab3a8576ed2fc"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/proxymsg/get_oss_config", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    if data["code"] == 0:
        AccessKeyId = data["data"]["AccessKeyId"]
        AccessKeySecret = data["data"]["AccessKeySecret"]
        SecurityToken = data["data"]["SecurityToken"]
        BucketName = data["data"]["BucketName"]
        Expiration = data["data"]["Expiration"]
        Endpoint = data["data"]["Endpoint"]
        CallbackUrl = data["data"]["CallbackUrl"]
        cdn = data["data"]["cdn"]
        
        if len(AccessKeyId) > 0:  
            auth = oss2.StsAuth(AccessKeyId, AccessKeySecret, SecurityToken)
            bucket = oss2.Bucket(auth, Endpoint, BucketName, connect_timeout=600)
            with open(file, "rb") as f:
                byte_data = f.read()
            file_name = Path(file).name
            publish_name = f"mecord/report/{file_name}" 
            bucket.put_object(publish_name, byte_data)
            return f"{cdn}{publish_name}" 
    else:
        logging.error(f"get_oss_config fail: response={data}")

def isTest():
    is_test = ""
    if "MECORD_IS_TEST" in os.environ:
        is_test = str(os.getenv("MECORD_IS_TEST"))

    is_test_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "env.txt")
    is_test_file = open(is_test_file_path, 'a+')
    is_test_file.seek(0, 0)
    line = is_test_file.readline()
    if line.startswith('MECORD_IS_TEST='):
        is_test = line[len('MECORD_IS_TEST='):]

    is_test_file.truncate(0)
    line = 'MECORD_IS_TEST={value}'.format(value=is_test)
    is_test_file.write(line)
    is_test_file.close()
    
    return len(is_test) > 0
# def isTest():
#     if os.getenv("MECORD_IS_TEST"):
#         return True
#     else:
#         return False