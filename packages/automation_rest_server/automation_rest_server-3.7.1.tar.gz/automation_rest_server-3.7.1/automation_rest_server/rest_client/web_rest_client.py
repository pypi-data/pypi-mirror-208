
import os
import yaml
import requests
from rest_client.resource.node_resource import NodeResource
from rest_client.resource.test_resource import TestResource
from rest_client.resource.web_resource import WebResource
from test_framework.state import NodeState
from test_framework.state import State
from utils import log


class WebRestClient(object):

    def __init__(self, time_out=20):
        self.session = requests.Session()
        host, port = self.get_web_server()
        self.node = NodeResource(host, port, self.session, time_out=time_out)
        self.test = TestResource(host, port, self.session, time_out=time_out)

    def get_web_server(self):
        config_file = os.path.join(os.path.dirname(__file__), '..', 'configuration', 'web_server.yaml')
        servers = yaml.load(open(config_file).read(), Loader=yaml.SafeLoader)
        ip, port = self.get_idle_server(servers)
        if ip is None:
            ip, port = servers[0]["host"], servers[0]["port"]
        return ip, port

    def get_idle_server(self, servers):
        ip, port = None, None
        for server in servers:
            web = WebResource(self.session)
            result = web.get_status(server["host"], server["port"])
            if result["state"] == State.PASS:
                ip = server["host"]
                port = server["port"]
                break
        return ip, port


def decorate_api_update_test_result(func):
    def func_wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        client = WebRestClient()
        client.test.update_test_result(args[1], args[2], args[3], args[4])
        log.INFO("decorate_api_update_test: {}: {}".format(args[1], State.verdicts_map[args[2]]))
        return ret
    return func_wrapper


def decorate_api_update_node_status(func):
    def func_wrapper(*args, **kwargs):
        is_updated, status = func(*args, **kwargs)
        if is_updated is True:
            client = WebRestClient()
            client.node.update_node_status(status)
            log.INFO("Rest API set node status to {}".format(NodeState.verdicts_map[status]))
        return is_updated, status
    return func_wrapper


def decorate_api_node_startup(func):
    def func_wrapper(*args, **kwargs):
        log.INFO("Rest API Node startup")
        client = WebRestClient()
        client.node.startup()
        log.INFO("Rest API Node startup Done")
        ret = func(*args, **kwargs)
        return ret
    return func_wrapper
