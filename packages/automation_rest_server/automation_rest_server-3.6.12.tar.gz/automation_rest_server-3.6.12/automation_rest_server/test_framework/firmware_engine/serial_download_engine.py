
import subprocess
import os
import time
from utils.system import decorate_exception_result
from utils.firmware_path import FirmwareBinPath
from utils import log


class PersesSerialDownloader(object):

    def __init__(self):
        self.fw_path_manage = FirmwareBinPath()
        self.root_path = os.getcwd()
        self.script_path = os.path.join(self.root_path, "Utility")
        self.logs_path = os.path.join(self.root_path, "Logs", "Two_step")
        self.orig_log_folders = list()
        self.latest_log_folders = list()
        self.log_file = None
        self.log_path = None
        # self.init_log_path()

    def init_log_path(self):
        if os.path.exists(self.logs_path) is False:
            os.mkdir(self.logs_path)

    def get_orig_logs(self):
        log_dirs = os.listdir(self.logs_path)
        for item in log_dirs:
            if os.path.isfile(os.path.join(self.logs_path, item)):
                self.orig_log_folders.append(os.path.join(self.logs_path, item))

    def gen_cmd_line(self, target_ip, com, cap, spi):
        command_line = f"cd /d {self.script_path} && python two_step_download.py --iroc={target_ip} " \
                       f"--firmwarePath={cap} --preBinPath={spi} --serialPort={com}"
        log.INFO(f"Perses two step: {command_line}")
        return command_line

    def get_new_log(self):
        self.latest_log_folders = os.listdir(self.logs_path)
        new_logs = list()
        for item in self.latest_log_folders:
            log_item = os.path.join(self.logs_path, item)
            if os.path.isfile(log_item):
                if log_item not in self.orig_log_folders:
                    new_logs.append(log_item)
        return new_logs

    @decorate_exception_result
    def run(self, parameters):
        ret = -1
        com_port = parameters["com"]
        target_ip = parameters.get("target_ip", None)
        spi_path = self.fw_path_manage.get_spi_path(parameters)
        cap_path = self.fw_path_manage.get_cap(parameters)
        if spi_path is not None and cap_path is not None and target_ip is not None:
            command_line = self.gen_cmd_line(target_ip, com_port, cap_path, spi_path)
            ret = os.system(command_line)
        logs = "pass" if ret == 0 else "fail"
        return ret, logs
