import sys
import os
import argparse
import urllib3
import logging
import shutil
import datetime

from pkg_resources import parse_version
import platform
from mecord import utils
from mecord.capability_provider import CapabilityProvider
from mecord import xy_user


parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
subparsers = parser.add_subparsers()
parser_widget = subparsers.add_parser("deviceid", help="获取当前设备ID")
parser_widget = subparsers.add_parser("set_multitask_num", help="设置同时处理任务数量")
parser_widget = subparsers.add_parser("get_multitask_num", help="获取同时处理任务数量")
parser_widget = subparsers.add_parser("unbind", help="取消mecord绑定的数据")
parser_widget = subparsers.add_parser("show_token", help="展示当前设备token")
parser_widget = subparsers.add_parser("add_token", help="填入其他设备token")
parser_widget = subparsers.add_parser("report", help="反馈")

parser_widget = subparsers.add_parser("widget", help="widget模块")
parser_widget.add_argument("init", type=str, default=None, help="创建widget, 注意: 需要在空目录调用")
parser_widget.add_argument("publish", type=str, default=None, help="发布模块")
parser_widget.add_argument("list", type=str, default=None, help="本地支持的widget列表")
parser_widget.add_argument("add", type=str, default=None, help="添加新的本地widget执行库")
parser_widget.add_argument("remove", type=str, default=None, help="删除指定的widget")
parser_widget.add_argument("pending_task", type=str, default=None, help="获取指定任务的待处理任务数量")

parser_service = subparsers.add_parser("service", help="service模块")
parser_service.add_argument("start", type=str, default=None, help="start task loop service")



def main():
    utils.get_salt()
    urllib3.disable_warnings()
    logFilePath = f"{os.path.dirname(os.path.abspath(__file__))}/log.log"
    if os.path.exists(logFilePath) and os.stat(logFilePath).st_size > (1024 * 1024 * 5):  # 5m bak file
        d = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        bakFile = logFilePath.replace(".log", f"_{d}.log")
        shutil.copyfile(logFilePath, bakFile)
        os.remove(logFilePath)

    if parse_version(platform.python_version()) >= parse_version("3.9.0"):
        logging.basicConfig(filename=logFilePath, 
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            encoding="utf-8",
                            level=logging.INFO)
    else:
        logging.basicConfig(filename=logFilePath, 
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            # encoding="utf-8",
                            level=logging.INFO)

    if len(sys.argv) >= 2:
        try:
            module = sys.argv[1]
            if len(module) != 0:
                CapabilityProvider().handle_action(module)
            else:
                print(f"Unknown command:{module}")
                print("Usage: mecord [deviceid|show_token|add_token|service|widget]")
                sys.exit(0)
        except Exception as e:
            print(f"uncatch Exception:{e}")
            return


# 重定向sys.stdout到LogStdout类的实例中
sys.stdout = utils.LogStdout()
if __name__ == '__main__':
    main()
sys.stdout.close()
