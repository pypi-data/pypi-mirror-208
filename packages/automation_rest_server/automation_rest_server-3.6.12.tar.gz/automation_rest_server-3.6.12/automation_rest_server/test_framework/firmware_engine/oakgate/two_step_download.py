
import os
from utils.system import decorate_exception_result
from utils.firmware_path import FirmwareBinPath
from utils import log


class OakgateTwoStepDownload(object):

    def __init__(self):
        self.root_path = os.getcwd()
        self.script_path = os.path.join(self.root_path, "Utility")
        self.root_log = os.path.join(self.root_path, "Logs")
        self.logs_path = os.path.join(self.root_log, "Two_step")
        self.orig_log_folders = list()
        self.latest_log_folders = list()
        self.fw_path_manage = FirmwareBinPath()

    def init_log_path(self):
        if os.path.exists(self.root_log):
            os.mkdir(self.root_log)
        if not os.path.exists(self.logs_path):
            os.mkdir(self.logs_path)

    def gen_two_step_cmd_line(self, fw_path, spi_fw, ogt, com):
        cmd = f"cd /d {self.script_path} && python two_step_download.py --oakgate {ogt} --firmwarePath {fw_path} " \
              f"--serialPort {com} --preBinPath {spi_fw}"
        log.INFO("oakgate two step download: {}".format(cmd))
        return cmd

    def get_orig_logs(self):
        log_dirs = os.listdir(self.logs_path)
        for item in log_dirs:
            if os.path.isfile(os.path.join(self.logs_path, item)):
                self.orig_log_folders.append(os.path.join(self.logs_path, item))

    def get_new_log(self, oakgate, com):
        new_logs = list()
        self.latest_log_folders = os.listdir(self.logs_path)
        for item in self.latest_log_folders:
            log_item = os.path.join(self.logs_path, item)
            if os.path.isfile(log_item):
                if log_item not in self.orig_log_folders:
                    if oakgate in log_item and com in log_item:    # check if this log belong to correct oagkate
                        new_logs.append(log_item)
        return new_logs

    @decorate_exception_result
    def run(self, parameters):
        cmd = None
        oakgate = parameters.get("oakgate", None)
        com = parameters.get("com", None)
        self.get_orig_logs()
        spi_path = self.fw_path_manage.get_spi_path(parameters)
        cap_path = self.fw_path_manage.get_cap(parameters)
        print(spi_path, cap_path, oakgate)
        if spi_path is not None and cap_path is not None and oakgate is not None and com is not None:
            cmd = self.gen_two_step_cmd_line(cap_path, spi_path, oakgate, com)
        if cmd is not None:
            ret = os.system(cmd)
            logs = self.get_new_log(oakgate, com)
        else:
            ret = -1
            logs = f"OGT upgrade fail: com: {com},ogt:{oakgate}"
        return ret, logs
