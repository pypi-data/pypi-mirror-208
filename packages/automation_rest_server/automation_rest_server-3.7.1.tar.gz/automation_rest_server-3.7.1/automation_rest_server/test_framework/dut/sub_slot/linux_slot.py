import platform
from tool.device.linux_nvme import LinuxNvme
from test_framework.state import SlotState
from utils.system import get_vendor_name
from utils import log


class LinuxSlot(object):

    def __init__(self):
        self.live_slots = list()
        self.nvme = LinuxNvme()

    def refresh(self, slot):
        dev_info = self.nvme.get_info(slot)
        slot_info = self._format_results(dev_info)
        log.INFO("refresh linux device %s", slot_info)
        return slot_info

    def _format_results(self, results):
        format_result = {
            "vendor": get_vendor_name(results["ssd_config_dic"]["vid"]),
            "fw_version": results["test_fw_config_dic"]["fw_public_revision"],
            "commit": results["test_fw_config_dic"]["fw_private_revision"][0:6],
            "ise/sed": results["ssd_config_dic"]["security_type"],
            "sn": results["ssd_config_dic"]["drive_sn"],
            "cap": self.convert_t(results["ssd_config_dic"]["drive_tnvmcap"]),
            "bb": results["drive_life_info_dic"]["count_grown_defects"],
            "max_ec": results["drive_life_info_dic"]["nand_max_erase_count"],
            "avg_ec": results["drive_life_info_dic"]["nand_avg_erase_count"],
            "status": SlotState.Idle
        }
        return format_result

    @staticmethod
    def convert_t(cap):
        return float('%.2f' % (cap/1000/1000/1000/1000))
