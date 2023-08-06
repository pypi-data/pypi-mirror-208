import os
from utils.system import decorate_exception_result
from utils.firmware_path import FirmwareBinPath
from utils import log
from utils.system import get_test_platform_version


class NVMeDownload(object):

    def __init__(self):
        self.root_path = os.getcwd()
        self.script_path = os.path.join(self.root_path, "Utility")
        self.logs_path = os.path.join(self.root_path, "Logs")
        self.orig_log_folders = list()
        self.latest_log_folders = list()
        self.fw_path_manage = FirmwareBinPath()

    def get_fw_path(self, parameters):
        nand = parameters.get("nand", "BICS5")
        commit = parameters.get("commit", "")
        fw_path = parameters.get("fw_path", "")
        if os.path.isfile(fw_path):
            win_fw_bin = fw_path
        else:
            win_fw_bin = self.fw_path_manage.get_image_path(fw_path, commit, nand)
        return win_fw_bin

    def gen_nvme_cmd_line(self, fw_path, ogt):
        version = get_test_platform_version()
        if version == 1:
            cmd = "cd /d {} && python cnex_auto_dl_fw.py --oakgate={} --image2={}".format(self.script_path, ogt, fw_path)
        else:
            cmd = "cd /d {} && python cnex_auto_dl_fw.py --oakgate={} --target_image={}".format(self.script_path, ogt, fw_path)
        log.INFO("oakgate download: {}".format(cmd))
        return cmd

    def get_orig_logs(self):
        log_dirs = os.listdir(self.logs_path)
        for item in log_dirs:
            if os.path.isdir(os.path.join(self.logs_path, item)):
                self.orig_log_folders.append(os.path.join(self.logs_path, item))

    def get_new_log(self, oakgate):
        new_logs = list()
        self.latest_log_folders = os.listdir(self.logs_path)
        for item in self.latest_log_folders:
            log_item = os.path.join(self.logs_path, item)
            if os.path.isdir(log_item):
                if log_item not in self.orig_log_folders:
                    for new_log_item in os.listdir(log_item):
                        if os.path.isfile(os.path.join(log_item, new_log_item)):
                            if oakgate in new_log_item:    # check if this log belong to correct oagkate
                                new_logs.append(os.path.join(log_item, new_log_item))
        return new_logs

    @decorate_exception_result
    def run(self, parameters):
        oakgate = parameters.get("oakgate", None)
        self.get_orig_logs()
        fw_path = self.fw_path_manage.get_fw_path_from_parameter(parameters)
        cmd = self.gen_nvme_cmd_line(fw_path, oakgate) if oakgate is not None and fw_path is not None else None
        if cmd is not None:
            ret = os.system(cmd)
            logs = self.get_new_log(oakgate)
        else:
            ret = -1
            logs = f"OGT upgrade fail: cmd: {cmd},ogt:{oakgate}"
        return ret, logs
