# coding=utf-8
import sys
import os
from flask_restful import Resource
from flask_restful import marshal_with
from rest_server.resource.models.helper import resource_fields
from test_framework.test_pool import TestPool
from utils.system import get_ip_address, get_automation_platform, get_linux_nvme_devs
from test_framework.state import State
from test_framework.state import NodeState


class StateResource(Resource):

    def __init__(self):
        self.test_pool = TestPool()

    @staticmethod
    def get_device_info():
        dev_list = list()
        if "win" not in sys.platform:
            system_name = "linux"
            dev_list = get_linux_nvme_devs()
        else:
            system_name = "windows"
        if not dev_list:
            dev = {"index": -1, "name": "not find device"}
            dev_list.append(dev)
        return system_name, dev_list

    @marshal_with(resource_fields, envelope='resource')
    def get(self, type_="ALL"):
        data = []
        state = NodeState.verdicts_map[self.test_pool.get_current_node_state()]
        ip_ = get_ip_address()
        system_name, dev_list = self.get_device_info()
        data.append(state)
        data.append(ip_)
        data.append(system_name)
        data.append(dev_list)
        data.append(get_automation_platform())
        result = {
            "data": data,
            "state": State.PASS
        }
        return result

    @marshal_with(resource_fields, envelope='resource')
    def post(self):
        result = {"msg": "update node state to DB", "state": State.PASS}
        return result
