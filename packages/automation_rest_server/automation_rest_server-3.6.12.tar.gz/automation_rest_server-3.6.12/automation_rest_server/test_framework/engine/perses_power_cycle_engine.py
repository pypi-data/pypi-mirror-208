import os
from utils import log
import time
import subprocess
from test_framework.state import State
from test_framework.engine.perses_engine import PersesEngine
from utils import log


class PersesPowerEngine(PersesEngine):

    def __init__(self):
        super(PersesPowerEngine, self).__init__()

    def update_fw_path(self, parameters):
        fw_path = parameters.get("fw_path", "")
        if fw_path != "":
            fw_path = self.fw_path_manage.change_path_linux_2_win(fw_path)
        parameters["fw_path"] = fw_path
        os.environ['fw_path'] = fw_path
        win_fw_path = self.fw_path_manage.get_fw_path_from_parameter(parameters)
        linux_path = self.fw_path_manage.change_path_win_2_linux(win_fw_path)
        parameters["fw_path"] = linux_path     # power cycle, need set linux path
        os.environ['fw_path'] = linux_path
        return parameters

    def run_test(self, test_case, parameters):
        parameters = self.update_fw_path(parameters)
        para_str = self.convert_para_2_string(parameters)
        if para_str == "":
            command_line = "python run.py powercycle -n {}".format(test_case)
        else:
            command_line = "python run.py powercycle -n {} -v {}".format(test_case, para_str)
        log.INFO("PersesPowerEngine run command: {}".format(command_line))
        child1 = subprocess.Popen(command_line, shell=True)
        return_code = child1.wait()
        return return_code
