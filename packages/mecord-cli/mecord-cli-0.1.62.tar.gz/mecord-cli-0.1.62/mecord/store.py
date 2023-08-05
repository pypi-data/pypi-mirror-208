import os
import json
from mecord import utils

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

@singleton
class Store(object):
    def __init__(self):
        dev = ""
        if utils.isTest():
            dev = "_test"
        uuid = utils.generate_unique_id()
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"data_{uuid}{dev}.json")

        #upgrade! data.json -> data_uuid_env.json
        old_datapath = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"data.json")
        if os.path.exists(old_datapath):
            olddata = {}
            with open(old_datapath, 'r') as f:
                olddata = json.load(f)
            with open(self.path, 'w') as f1:
                json.dump(olddata, f1)
            os.remove(old_datapath)
        
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump({}, f)
                
    def read(self):
        with open(self.path, 'r') as f:
            data = json.load(f)
            
        return data
    
    def write(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f)


def groupUUID():
    sp = Store()
    read_data = sp.read()
    if "groupUUID" in read_data:
        return read_data["groupUUID"]
    else:
        return ""
    
def isCreateWidget():
    sp = Store()
    read_data = sp.read()
    if "isCreateWidget" in read_data:
        return read_data["isCreateWidget"]
    else:
        return False
    
def finishCreateWidget():
    sp = Store()
    read_data = sp.read()
    read_data["isCreateWidget"] = False
    sp.write(read_data)
    
def token():
    sp = Store()
    read_data = sp.read()
    if "token" in read_data:
        return read_data["token"]
    else:
        return ""
    
def multitaskNum():
    sp = Store()
    read_data = sp.read()
    if "multitasking_num" in read_data:
        return read_data["multitasking_num"]
    else:
        return 1

def setMultitaskNum(num):
    sp = Store()
    read_data = sp.read()
    read_data["multitasking_num"] = num
    sp.write(read_data)
    
def widgetMap():
    sp = Store()
    read_data = sp.read()
    if "widgets" in read_data:
        return read_data["widgets"]
    else:
        return {}
    
def insertWidgets(widget_id, path):
    sp = Store()
    read_data = sp.read()
    if "widgets" not in read_data:
        read_data["widgets"] = {}
    widgetsMap = read_data["widgets"]
    widgetsMap[widget_id] = path
    for k in list(widgetsMap.keys()):
        if os.path.exists(widgetsMap[k]) == False:
            del widgetsMap[k]
    sp.write(read_data)

def writeDeviceInfo(data):
    sp = Store()
    read_data = sp.read()
    read_data["deviceInfo"] = data
    sp.write(read_data)
    
def readDeviceInfo():
    sp = Store()
    read_data = sp.read()
    if "deviceInfo" in read_data:
        return read_data["deviceInfo"]
    else:
        return {}

def clear():
    sp = Store()
    sp.write({})