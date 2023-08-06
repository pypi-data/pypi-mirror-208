import os
import yaml
from utils import log


class PersesSlot(object):

    def __init__(self):
        self.root_path = os.getcwd()

    def refresh(self, slot=None, block=None):
        dut_dict = None
        if slot is not None:
            cmd = f"cd {self.root_path} && python3 run.py testfile debug_dut.py -s {slot}"
        elif block is not None:
            cmd = f"cd {self.root_path} && python3 run.py testfile debug_dut.py -b {block}"
        else:
            cmd = f"cd {self.root_path} && python3 run.py testfile debug_dut.py"
        log.INFO(cmd)
        ret = os.system(cmd)
        if ret == 0:
            dut_yaml = os.path.join(self.root_path, "log", "dut.yaml")
            if os.path.exists(dut_yaml):
                dut_dict = yaml.load(open(dut_yaml).read(), Loader=yaml.FullLoader)
                log.INFO(dut_dict)
        return dut_dict


