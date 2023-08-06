import os
import yaml
import subprocess
from utils import log
from utils.system import get_ip_address
from test_framework.state import State
from utils.firmware_path import FirmwareBinPath


class VenusEngine(object):

    def __init__(self):
        self.working_path = os.environ["working_path"]
        self.prun_port = os.environ["prun_port"]
        self.log_path = self.get_log_path()
        self.orig_log_folders = ""
        self.fw_path_manage = FirmwareBinPath()

    def get_log_path(self):
        log_path = os.path.join(self.working_path, "log")
        if os.path.exists(log_path) is False:
            os.mkdir(log_path)
        if os.path.exists(log_path) is False:
            os.mkdir(log_path)
        return log_path

    def get_new_log(self, test_case):
        test_name = test_case.split('.')[-1]
        latest_log_folders = os.listdir(self.log_path)
        orig_log_folders = self.read_orig_logs()
        new_logs = []
        for item in latest_log_folders:
            if item not in orig_log_folders:
                item_path = os.path.join(self.log_path, item)
                if os.path.isfile(item_path) and test_name in item:
                    new_logs.append(item_path)
                elif os.path.isdir(item_path):
                    for temp_log in os.listdir(item_path):
                        temp_log_path = os.path.join(item_path, temp_log)
                        if os.path.isfile(temp_log_path):
                            new_logs.append(temp_log_path)
        return new_logs

    def get_orig_logs(self):
        self.orig_log_folders = os.path.join(self.log_path, "org_logs_{}.yaml".format(self.prun_port))
        orig_log_folders = os.listdir(self.log_path)
        with open(self.orig_log_folders, 'w') as f:
            yaml.dump(orig_log_folders, f)

    def read_orig_logs(self):
        with open(self.orig_log_folders) as f:
            log_folders = yaml.load(f.read(), Loader=yaml.SafeLoader)
        return log_folders

    @staticmethod
    def convert_para_2_string(parameters):
        para_str = ""
        for key, value in parameters.items():
            temp = "{}:{}".format(key, value)
            if para_str == "":
                para_str = temp
            else:
                para_str = "{},{}".format(para_str, temp)
        return para_str

    def run_test(self, test_case, parameters):
        parameters = self.fw_path_manage.update_perses_fw_path(parameters)
        print("venus para", parameters)
        para_str = self.convert_para_2_string(parameters)
        log.INFO("venus para str {}".format(para_str))
        if para_str == "":
            command_line = "python run.py testcase -n {}".format(test_case)
        else:
            command_line = "python run.py testcase -n {} -v {}".format(test_case, para_str)
        log.INFO("Venus Engine run command: {}".format(command_line))
        child1 = subprocess.Popen(command_line, shell=True)
        return_code = child1.wait()
        return return_code

    def run(self, test_case, test_path, parameters, queue):
        log.INFO("venus run")
        self.get_orig_logs()
        ret_code = self.run_test(test_case, parameters)
        logs = self.get_new_log(test_case)
        if ret_code == 0:
            test_result = State.PASS
        elif ret_code == 1:
            test_result = State.FAIL
        elif ret_code == 2:
            test_result = State.BLOCK
        elif ret_code == 3:
            test_result = State.ERROR_NOT_FOUND
        elif ret_code == 10:
            test_result = State.ERROR_UNHEALTHY
        elif ret_code == 99:
            test_result = State.ERROR_BASE_EXCEPTION
        else:
            test_result = State.BLOCK
        result = {"name": test_case, "result": test_result, "log": logs}
        print("testcase: {}".format(test_case), result)
        queue.put(result)
        return ret_code
