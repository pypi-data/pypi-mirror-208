import os
import re
import platform
from test_framework.dut.sub_slot.oakgate_slot import OakgateSlot
from test_framework.dut.sub_slot.linux_slot import LinuxSlot
from test_framework.dut.sub_slot.perses_slot import PersesSlot
from test_framework.dut.sub_slot.powercycle_slot import PowercycleSlot
from utils.system import get_automation_platform, get_ip_address
from rest_client.web_rest_client import WebRestClient
from rest_client.resource.models.helper import State
from utils import log


class Slot(object):

    def __init__(self):

        self.rest_client = WebRestClient()
        self.platform = get_automation_platform()
        self.ip = get_ip_address()
        self.port = os.environ.get("prun_port")
        self.node_id = None

    def get_config_from_web(self):
        config = dict()
        result = self.rest_client.node.get_node(self.ip, self.port)
        print(result)
        if result["state"] == State.PASS:
            if result["data"]:
                self.node_id = result["data"][0]["id"]
                config = self.parse_node_parameters(result["data"][0]["parameters"])
        return config

    @staticmethod
    def parse_node_parameters(para_string):
        para = dict()
        para_list = para_string.split(";")
        for item in para_list:
            rets = re.findall(r"(\w+)\:(.+)", item)
            if rets:
                para[rets[0][0]] = rets[0][1]
        return para

    def refresh(self):
        config = self.get_config_from_web()
        print("Get node config from web", config)
        slot_info = None
        if self.platform == "oakgate":
            if "oakgate" in config.keys():
                slot_info = self.oakgate_refresh(config["oakgate"])
            else:
                log.INFO("DUT did not find oakgate setting, skip update DUT")
        elif self.platform == "perses":
            slot_info = self.perses_refresh(config)

        if slot_info is not None:
            self.rest_client.node.update_dut_info(self.node_id, slot_info)
        return slot_info

    @staticmethod
    def oakgate_refresh(config_name):
        oak_slot = OakgateSlot(config_name)
        return oak_slot.refresh()

    @staticmethod
    def perses_refresh(config):
        slot = config.get("slot", None)
        target_ip = config["target_ip"] if "target_ip" in config.keys() else None
        try:
            if "win" not in platform.system().lower():
                log.INFO("Start scan Linux DUT information")
                linux_slot = PersesSlot()
                return linux_slot.refresh(slot=slot)
            else:
                if target_ip is None:
                    log.WARN("Windows not support scan DUT information")
                    return None
                else:
                    log.INFO("Start scan Powercycle DUT information")
                    powercycle_slot = PowercycleSlot()
                    return powercycle_slot.refresh(config)
        except Exception as err:
            log.WARN(err)
