
import subprocess
import os
import time
from multiprocessing import Queue
from utils.system import decorate_exception_result
from test_framework.engine.perses_power_cycle_engine import PersesPowerEngine
from test_framework.test_base import TestBase
from utils import log
from utils.firmware_path import FirmwareBinPath
from test_framework.state import State


class PersesDownloader(TestBase):

    def __init__(self):
        super(PersesDownloader, self).__init__()
        self.root_path = os.getcwd()
        self.power_engine = PersesPowerEngine()
        self.fw_path_manage = FirmwareBinPath()
        self.download_testcase = "test_debug:TestPowerCycleDebug.test_fw_upgrade_with_clearspi"

    @decorate_exception_result
    def run(self, parameters):
        queue = Queue()
        test_path = self.get_all_script_path(self.download_testcase)
        if test_path:
            for index in range(1):
                log.INFO("########Perses Download test path: {}, loop: {}".format(test_path[0], index))
                self.power_engine.run(self.download_testcase, test_path[0], parameters, queue)
                result = queue.get(True)
                logs = result["log"]
                if result["result"] == State.PASS:
                    log.INFO("########test passed: {}".format(index))
                    ret = 0
                    break
                ret = -1
        else:
            ret = State.ERROR_NOT_FOUND
            logs = "NOT find test case: {}".format(self.download_testcase)
        return ret, logs

