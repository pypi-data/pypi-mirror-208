# coding=utf-8
# pylint: disable=import-error,eval-used
import json
import os
import sys
from rest_client.resource.models.helper import rest_get_call, rest_post_json_call
from utils.system import get_ip_address, get_automation_platform


class NodeResource(object):

    def __init__(self, host, port, session, time_out):
        self.host = host
        self.port = port
        self.session = session
        self.time_out = time_out

    def get_node(self, ip, port):
        url_ = "http://{0}:{1}/api/node/{2}/{3}".format(self.host, self.port, ip, port)
        result = rest_get_call(url_, self.session, self.time_out)
        return result

    def update_node_status(self, status):
        ip = get_ip_address()
        port = os.environ.get("prun_port", 5000)
        url_ = "http://{0}:{1}/api/node/status/{2}/{3}/{4}".format(self.host, self.port, ip, port, status)
        result = rest_post_json_call(url_, self.session, "", self.time_out)
        return result

    def update_dut_info(self, dut_id, dut_info):
        url_ = "http://{0}:{1}/api/node/{2}".format(self.host, self.port, dut_id)
        result = rest_post_json_call(url_, self.session, json.dumps(dut_info), self.time_out)
        return result

    def startup(self):
        ip = get_ip_address()
        port = os.environ.get("prun_port", 5000)
        node_info = {
            "platform": get_automation_platform(),
            "system": "windows" if "win" in sys.platform else "linux"
        }
        url_ = "http://{0}:{1}/api/node/startup/{2}/{3}".format(self.host, self.port, ip, port)
        result = rest_post_json_call(url_, self.session, json.dumps(node_info), self.time_out)
        return result

#
# if __name__ == '__main__':
#     session1 = requests.Session()
#     node = NodeResource("127.0.0.1", "8000", session1, 10)
#     get_nodes = node.get_node("172.29.128.176", "5000")
#     pass


