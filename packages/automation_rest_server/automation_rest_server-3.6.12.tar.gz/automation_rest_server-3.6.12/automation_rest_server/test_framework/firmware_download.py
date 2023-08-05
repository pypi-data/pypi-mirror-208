
from multiprocessing import Queue
from test_framework.state import State, DownloadType
from test_framework.firmware_engine.oakgate_download_engine import OakgateDownloader
from test_framework.firmware_engine.perses_download_engine import PersesDownloader
from test_framework.firmware_engine.logic_with_firmware_engine import LogicFWDownloader
from utils.process import MyProcess
from utils.system import get_automation_platform
from tool.git.git_operator import GitOperator
from utils import log


class FirmwareDownloader(object):

    def __init__(self, execute_name):
        self.process_run_ = None
        self.results = list()
        self.execute_name = execute_name
        self.runner = None

    def get_download_engine(self, test_parameters):
        if int(test_parameters["upgrade_type"]) in [DownloadType.two_step_download, DownloadType.NVMe]:
            platform = get_automation_platform()
            if platform == "oakgate":
                self.runner = OakgateDownloader()
            elif platform == "perses":
                self.runner = PersesDownloader()
        elif int(test_parameters["upgrade_type"]) == DownloadType.logic_fw:
            self.runner = LogicFWDownloader()
            
    @staticmethod
    def update_git(parameters):
        if "git_version" in parameters.keys():
            user = parameters["git_user"]
            passwd = parameters["git_key"]
            git_version = parameters["git_version"]
            log.INFO(f"Git update: user: {user}, passwd: {passwd}, version: {git_version}")
            git = GitOperator(user, passwd)
            msg, ret = git.update_latest_code(git_version)
            log.INFO(f"Git update result:  {ret}, msg: {msg}")

    def _run(self, test_parameters, queue):
        try:
            self.get_download_engine(test_parameters)
            if self.runner is not None:
                status, msg = self.runner.run(test_parameters)
                ret = State.PASS if status == 0 else State.FAIL
                result = {"name": self.execute_name, "result": ret, "log": msg}
            else:
                result = {"name": self.execute_name, "result": State.FAIL, "log": "prun start in wrong path"}
            queue.put(result)
        except Exception as e:
            log.INFO(e)
            result = None
        return result

    def run(self, test_parameters):
        log.INFO("firmware download parameters:")
        print(test_parameters)
        self.update_git(test_parameters)
        queue = Queue()
        self.process_run_ = MyProcess(target=self._run, args=(test_parameters, queue, ))
        self.process_run_.start()
        self.process_run_.join()
        value = queue.get(True)
        self.results.append(value)
        return self.results

    def stop(self):
        print("FirmwareDownloader runner . stop")
        if self.process_run_ is not None:
            ret = self.process_run_.stop()
        else:
            ret = -1
        return ret