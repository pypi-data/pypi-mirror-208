
import os
import platform
from multiprocessing import Queue
from utils.system import decorate_exception_result
from test_framework.engine.perses_engine import PersesEngine
from test_framework.firmware_engine.serial_download_engine import PersesSerialDownloader
from test_framework.test_base import TestBase
from test_framework.state import State, UpgradeType
from utils import log


class PersesDownloader(TestBase):

    def __init__(self):
        super(PersesDownloader, self).__init__()
        self.root_path = os.getcwd()
        self.download_testcase = "test_debug:TestPowerCycleDebug.test_auto_fw_upgrade"

    def nvme_download(self, parameters):
        queue = Queue()
        ret, logs = -1, ""
        test_path = self.get_all_script_path(self.download_testcase)
        if test_path:
            for index in range(1):
                log.INFO("########Perses Download test path: {}, loop: {}".format(test_path[0], index))
                perses_engine = PersesEngine()
                perses_engine.run(self.download_testcase, test_path[0], parameters, queue)
                result = queue.get(True)
                logs = result["log"]
                if result["result"] == State.PASS:
                    log.INFO("########test passed: {}".format(index))
                    ret = 0
                    break
        else:
            ret = State.ERROR_NOT_FOUND
            logs = "NOT find test case: {}".format(self.download_testcase)
        return ret, logs

    @staticmethod
    def two_step_download(parameters):
        engine = PersesSerialDownloader()
        ret, logs = engine.run(parameters)
        return ret, logs

    @decorate_exception_result
    def run(self, parameters):
        if int(parameters.get("upgrade_type", 1)) == UpgradeType.NVMe[0]:
            ret, logs = self.nvme_download(parameters)
        else:
            ret, logs = self.two_step_download(parameters)
        return ret, logs

