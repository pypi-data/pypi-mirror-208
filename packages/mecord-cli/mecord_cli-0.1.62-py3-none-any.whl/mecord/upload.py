import requests
import os
from urllib.parse import *

from mecord import xy_pb
from mecord import utils
from pathlib import Path

def upload(src):
    file_name = Path(src).name
    ossurl, content_type = xy_pb.GetOssUrl(os.path.splitext(file_name)[-1][1:])
    if len(ossurl) == 0:
        print("oss server is not avalid")
        return ""

    headers = dict()
    headers['Content-Type'] = content_type
    requests.adapters.DEFAULT_RETRIES = 3
    s = requests.session()
    s.keep_alive = False
    res = s.put(ossurl, data=open(src, 'rb').read(), headers=headers)
    s.close()
    if res.status_code == 200:
        realOssUrl = urljoin(ossurl, "?s")
        return realOssUrl
    else:
        print(f"upload file fail! res = {res}")
        return ""

def uploadWidget(src, widgetid):
    ossurl, content_type = xy_pb.GetWidgetOssUrl(widgetid)
    if len(ossurl) == 0:
        print("oss server is not avalid")
        return "", -1
    
    headers = dict()
    headers['Content-Type'] = content_type
    requests.adapters.DEFAULT_RETRIES = 3
    s = requests.session()
    s.keep_alive = False
    res = s.put(ossurl, data=open(src, 'rb').read(), headers=headers)
    s.close()
    if res.status_code == 200:
        realOssUrl = urljoin(ossurl, "?s")
        checkid = xy_pb.WidgetUploadEnd(realOssUrl)
        if checkid > 0:
            return realOssUrl, checkid
        else:
            return "", -1
    else:
        print(f"upload file fail! res = {res}")
        return "", -1

# utils.mecordPrint(urljoin("http://yesdesktop-web-beta.oss-cn-shenzhen.aliyuncs.com/uploads/aigc/widgets/9475cb02-becb-45de-8656-ebe0204201b2/9475cb02-becb-45de-8656-ebe0204201b2.zip?Expires=1678705199&OSSAccessKeyId=LTAI5tGmTwAZJEzGL38wAjXV&Signature=uDvQJUs83WQ1ZU9dbMcHTw6zuDQ=", "?s"))
# utils.mecordPrint(upload("E:\\aigc\\mecord_python\\publish_mecord_pip.zip", "application/zip"))
# utils.mecordPrint(uploadWidget("E:\\aigc\\mecord_python\\publish_mecord_pip.zip", "fac64812-23c1-4a37-8e99-ddc4fb4d2a01"))