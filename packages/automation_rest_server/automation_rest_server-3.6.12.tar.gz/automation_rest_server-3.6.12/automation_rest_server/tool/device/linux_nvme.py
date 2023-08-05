import sys
import re
if "win" not in sys.platform.lower():
    from tool.device.nvme.nvme import Tahoe
from utils.system import execute


class LinuxNvme(object):

    def __init__(self):
        pass

    @staticmethod
    def get_info(slot=None):
        driver = Tahoe(slot=slot)
        information = driver.get_info()
        return information

    @staticmethod
    def get_linux_nvme_devs():
        dev_list = list()
        control_list = list()
        cmd = "ls /dev/n*"
        _, outs = execute(cmd, console=False)
        rets = re.findall("/dev/(nvme(\d+))\s", outs, re.DOTALL)
        for item in rets:
            if item[1] not in control_list:
                dev = {"ctrl_id": item[1], "name": item[0]}
                control_list.append(item[1])
                dev_list.append(dev)
        return dev_list
