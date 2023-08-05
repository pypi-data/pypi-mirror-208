import sys
import os
from mecord.public_tools.decorator_tools import singleton
from mecord import xy_user
from mecord import mecord_service
from mecord import mecord_widget
from mecord import store
from mecord import utils

# sys.path.append("..")
from mecord import xy_pb

from pkg_resources import get_distribution
import threading


@singleton
class CapabilityProvider:

    def __init__(self):
        self.max_check_device_count = 300  # loop waiting 5min
        self.cur_check_device_count = 0

    def service(self):
        if xy_user.User().isLogin() == False:
            print('please login first! \nUsage: mecord deviceid & Use Mecord Application scan it')
            return
        wid_map = store.widgetMap()
        if len(wid_map) == 0:
            print("please add widget first! \nUsage: mecord widget add [widget python path]")
            return
        if len(sys.argv) <= 2:
            print('please set command! Usage: mecord service start')
            return

        command = sys.argv[2]
        service = mecord_service.MecordService()
        if command == 'start':
            if service.is_running():
                print('Service is already running.')
            else:
                print('Starting service...')
                service.start()
        elif command == 'stop':
            if not service.is_running():
                print('Service is not running.')
            else:
                print('Stopping service...')
                service.stop()
        elif command == 'restart':
            print('Restarting service...')
            service.restart()
        elif command == 'status':
            if service.is_running():
                print('Service is running.')
            else:
                print('Service is not running.')
        else:
            print("Unknown command:", command)
            print("Usage: python service.py [start|stop|restart|status]")

    def widget(self):
        if xy_user.User().isLogin() == False:
            print('please login first! \nUsage: mecord deviceid & Use Mecord Application scan it')
            return
        if len(sys.argv) <= 2:
            print('please set command! Usage: mecord widget [init|publish]')
            return

        command = sys.argv[2]
        work_path = os.getcwd()
        if len(sys.argv) > 3:
            work_path = sys.argv[3]
        if command == 'init':
            mecord_widget.createWidget(work_path)
        elif command == 'publish':
            mecord_widget.publishWidget(work_path)
        elif command == 'list':
            map = store.widgetMap()
            if len(map) == 0:
                print("local widget is empty")
            maxJust = 20
            for it in map:
                if len(it) > maxJust:
                    maxJust = len(it)
            for it in map:
                print(f"{it.ljust(maxJust + 4)} {map[it]}")
        elif command == 'add':
            mecord_widget.addWidgetToEnv(work_path)
        elif command == 'remove':
            mecord_widget.remove(work_path)
        elif command == 'pending_task':
            mecord_widget.getTaskCount(work_path)
        else:
            utils.mecordPrint("Unknown command:", command)
            print("Usage: mecord widget [init|publish|list|add|remove|pending_task]")

    def checkDeviceInfo(self):

        if self.cur_check_device_count > self.max_check_device_count:
            return
        if xy_pb.GetAigcDeviceInfo():
            if store.isCreateWidget():
                mecord_widget.createDemoWidget()
        else:
            self.cur_check_device_count += 1
            threading.Timer(1, self.checkDeviceInfo, ()).start()

    def unbind(self):
        xy_pb.DeviceUnbind()
        store.clear()
        print(f"your device is return to initialization state!")

    def deviceid(self):
        store.writeDeviceInfo(utils.deviceInfo())
        xy_user.User().loginIfNeed()
        uuid = utils.generate_unique_id()
        qrcode_str = f"https://main_page.html?action=scanbind&deviceId={uuid}"
        utils.displayQrcode(qrcode_str)
        print(f"deviceid    : {uuid}")
        print(f"scan-qrcode : {qrcode_str}")
        if xy_user.User().isLogin() == False:
            print(f"waiting for scan...")
        self.cur_check_device_count = 0
        self.checkDeviceInfo()

    def joinToken(self):
        if len(sys.argv) <= 2:
            print('can not found token! Usage: mecord add_token {token}')
            return
        if xy_pb.ExpansionWithToken(sys.argv[2]):
            print('success')

    def showToken(self):
        t = store.token()
        if len(t) > 0:
            print(f"your token is : {t}")
            utils.displayQrcode(t)
        else:
            print(f"not have token")

    def setMultitaskNum(self):
        if len(sys.argv) <= 2:
            print('please set multitasking number')
            return
        if sys.argv[2].isdigit() == False:
            print('multitasking number is not digit')
            return
        if sys.argv[2] < 1:
            print(f'multitasking number illegal, {sys.argv[2]} must be greater than 1')
            return
        store.setMultitaskNum(sys.argv[2])
        print(f"multitasking number is {sys.argv[2]}")

    def getMultitaskNum(self):
        t = store.multitaskNum()
        print(f"multitasking number is {t}")

    def report(self):
        utils.reportLog()
        print(f"report success")

    def version(self):
        ver = get_distribution("mecord-cli").version
        test_env = ""
        if os.getenv("MECORD_IS_TEST"):
            test_env = f",test"
        salt = utils.get_salt()
        salt_env = ""
        if len(salt.strip()) > 0:
            salt_env = f",salt={salt}"
        print(f"version is {ver}{test_env}{salt_env}")

    def salt(self):
        if len(sys.argv) <= 2:
            print('please set command! Usage: mecord salt [value]')
            return
        value = sys.argv[2]

        salt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salt.txt")
        salt_file = open(salt_file_path, 'a+')
        salt_file.truncate(0)
        line = 'MECORD_DEVICEID_SALT={vvalue}'.format(vvalue=value)
        salt_file.write(line)
        salt_file.close()

    def handle_action(self, str_n):
        if str_n == "widget":
            self.widget()
        elif str_n == "service":
            self.service()
        elif str_n == "deviceid":
            self.deviceid()
        elif str_n == "unbind":
            self.unbind()
        elif str_n == "show_token":
            self.showToken()
        elif str_n == "add_token":
            self.joinToken()
        elif str_n == "set_multitask_num":
            self.setMultitaskNum()
        elif str_n == "get_multitask_num":
            self.getMultitaskNum()
        elif str_n == "report":
            self.report()
        elif str_n == "version":
            self.version()
        elif str_n == "salt":
            self.salt()

