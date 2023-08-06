
import os
import yaml
from utils import log
from utils.system import get_vendor_name
from utils.system import get_test_platform_version


class OakgateSlot(object):

    def __init__(self, config_name):
        self.config_name = config_name
        self.orig_log_folders = list()
        self.platform_path = os.environ.get('working_path')
        self.logs_path = os.path.join(self.platform_path, "Logs")
        self.script = "u_ssd_data_collection"

    def execute_command(self, config_name):
        version = get_test_platform_version()
        if version == 1:
            command_line = "cd /d {} && python run.py --oakgate {} --script {}.py".\
                format(self.platform_path, config_name, self.script)
        else:
            command_line = "cd /d {} && python run.py --device {} --test {}.py".\
                format(self.platform_path, config_name, self.script)

        log.INFO("Oakgate execute command: {}".format(command_line))
        return os.system(command_line)

    def get_orig_logs(self):
        all_logs = os.listdir(self.logs_path)
        self.orig_log_folders = [item for item in all_logs if self.script in item]

    def get_new_logs(self):
        latest_log_folders = os.listdir(self.logs_path)
        new_logs = list()
        for item in latest_log_folders:
            if item not in self.orig_log_folders:
                if os.path.isdir(os.path.join(self.logs_path, item)):
                    if self.script in item:
                        new_logs.append(item)
        return new_logs

    def load_result(self):
        format_result = dict()
        logs = self.get_new_logs()
        if logs:
            files = os.listdir(os.path.join(self.logs_path, logs[0]))
            for item in files:
                if "SSD_data.yaml" in item:
                    log.INFO("Find command output yaml: {}".format(item))
                    with open(os.path.join(self.logs_path, logs[0], item), encoding='utf-8') as f:
                        results = yaml.safe_load(f)
                        format_result = self._format_results(results)
        log.INFO("get result:")
        print(format_result)
        return format_result

    def _format_results(self, results):
        format_result = {
            "vendor": get_vendor_name(results["ssd_config_dic"]["drive_vid"]),
            "fw_version": results["test_fw_config_dic"]["fw_public_revision"],
            "commit": results["test_fw_config_dic"]["fw_private_revision"],
            "ise/sed": results["ssd_config_dic"]["security_type"],
            "sn": results["ssd_config_dic"]["drive_sn"],
            "cap": self.convert_t(results["ssd_config_dic"]["drive_tnvmcap"]),
            "bb": "{}".format(results["drive_life_info_dic"]["count_grown_defects"]),
            "max_ec": results["drive_life_info_dic"]["nand_max_erase_count"],
            "avg_ec": results["drive_life_info_dic"]["nand_avg_erase_count"],
            "cpd": results["drive_life_info_dic"]["count_primary_defects"],
            "min_ec": results["drive_life_info_dic"]["nand_min_erase_count"],

        }
        return format_result

    @staticmethod
    def convert_t(cap):
        return "" if cap == "" else float('%.2f' % (cap/1000/1000/1000/1000))

    def refresh(self):
        result = None
        self.get_orig_logs()
        ret = self.execute_command(self.config_name)
        if ret == 0:
            result = self.load_result()
        return result
