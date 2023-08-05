# coding=utf-8
# pylint: disable=import-error,eval-used
import json
import time
from utils import log
from rest_client.resource.models.helper import rest_get_call, rest_post_json_call
from test_framework.test_result import TestResult
from test_framework.state import TestType, State


class TestResource(object):

    def __init__(self, host, port, session, time_out):
        self.host = host
        self.port = port
        self.session = session
        self.time_out = time_out
        self.test_result = TestResult()

    def update_test_result(self, test_key, status, result, test_type):
        url_ = "http://{0}:{1}/api/result/{2}/{3}".format(self.host, self.port, TestType.url_map[test_type], test_key)
        data = {"msg": self.get_test_log(result), "state": status, "data": result}
        max_count = 10
        index = 0
        while index < max_count:
            ret = rest_post_json_call(url_, self.session, json.dumps(data), self.time_out)
            if ret["state"] == State.PASS:
                break
            else:
                time.sleep(5)
                log.INFO("Send result failed ret: {}, try again, index:{}".format(ret, index))
                index += 1
        return ret

    def get_test_log(self, result):
        logs = self.test_result.get_test_suite_test_msg(result)
        return logs
