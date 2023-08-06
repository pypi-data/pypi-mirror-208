import os
import subprocess
from utils import log
from test_framework.engine.special_parameter import Parameters
from test_framework.state import State
from utils.firmware_path import FirmwareBinPath
from utils.system import get_test_platform_version


class OakgateEngine(object):

    def __init__(self):
        self.orig_log_folders = None
        self.latest_log_folders = None
        self.root_path = os.environ["working_path"]
        self.run_path = os.path.join(self.root_path, "run.py")
        self.logs_path = os.path.join(self.root_path, "Logs")
        self.create_logs_folder()
        self.parm = Parameters()
        self.fw_path_manage = FirmwareBinPath()

    def change_test_parameter(self, parameters):
        test_platform_version = get_test_platform_version()
        if test_platform_version == 2:
            test_name = parameters["script"]
            parameters["test"] = test_name
            parameters = self.parm.pop_parm(parameters, "script")
            if "image1" in parameters.keys():
                parameters["base_image"] = parameters["image1"]
                parameters.pop["image1"]
            if "image2" in parameters.keys():
                parameters["target_image"] = parameters["image2"]
                parameters.pop["image2"]
        return parameters

    def generate_command(self, parameters):
        command_line = str()
        image_parameters = self.fw_path_manage.generate_oakgate_images(parameters)
        parameters.update(image_parameters)
        parameters = self.parm.pop_parm(parameters, "volume")
        parameters = self.parm.pop_parm(parameters, "base_path")
        parameters = self.parm.pop_parm(parameters, "nand")
        parameters = self.change_test_parameter(parameters)
        for key, value in parameters.items():
            temp_command = "--{} {} ".format(key, value)
            command_line = command_line + temp_command
        command_ = "cd {} && python run.py {}".format(self.root_path, command_line)
        print(parameters, command_)
        return command_

    def create_logs_folder(self):
        if os.path.exists(self.logs_path) is False:
            os.mkdir(self.logs_path)

    def get_new_log(self, test_case):
        self.latest_log_folders = os.listdir(self.logs_path)
        test_name = test_case.split('.')[0]
        new_logs = list()
        for item in self.latest_log_folders:
            if item not in self.orig_log_folders:
                if os.path.isdir(os.path.join(self.logs_path, item)):
                    if test_name in item:
                        new_logs.append(item)
        return new_logs

    def get_orig_logs(self):
        self.orig_log_folders = os.listdir(self.logs_path)

    def get_logs(self, log_path):
        log_content = str()
        if os.path.exists(log_path):
            log = open(log_path)
            log_content = log.read()
            log.close()
        return log_content

    def get_test_log(self, test_case):
        logs = list()
        new_logs = self.get_new_log(test_case)
        for log_folder in new_logs:
            temp_folder = os.path.join(self.logs_path, log_folder)
            for log_file in os.listdir(temp_folder):
                log_path = os.path.join(temp_folder, log_file)
                if log_file.endswith(".log") or log_file.endswith(".txt"):
                    logs.append(log_path)
        return logs

    def run(self, test_case, test_path, parameters, queue):
        test_platform_version = get_test_platform_version()
        fail_return_code = 100 if test_platform_version == 2 else 1
        fail_keep_env_code = 3
        if "key" in parameters.keys():
            parameters.pop("key")
        print(parameters)
        try:
            command_ = self.generate_command(parameters)
            self.get_orig_logs()
            popen = subprocess.Popen(command_, shell=True)  # stdout=subprocess.PIPE, stderr=subprocess.PIPE
            popen.communicate()
            ret_code = popen.returncode
            logs = self.get_test_log(test_case)
            log.INFO(f"test-platform return code: {ret_code}")
            if ret_code == 0:
                test_result = State.PASS
            elif ret_code == fail_return_code or ret_code == fail_keep_env_code:
                test_result = State.FAIL
            elif ret_code == 10:
                test_result = State.ERROR_UNHEALTHY
            else:
                test_result = State.BLOCK
        except Exception as e:
            log.ERR("Run test-platform exception")
            log.ERR(e)
            test_result = State.ERROR_BASE_EXCEPTION
            logs = ""
            ret_code = 1
        result = {"name": test_case, "result": test_result, "log": logs}
        print(result)
        queue.put(result)
        return ret_code
