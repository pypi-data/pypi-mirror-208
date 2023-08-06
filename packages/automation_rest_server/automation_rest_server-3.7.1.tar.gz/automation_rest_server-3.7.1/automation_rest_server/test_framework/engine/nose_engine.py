import os
import time
import subprocess
import yaml
from test_framework.state import State
from utils import log


class NoseEngine(object):

    def __init__(self):
        self.prun_port = os.environ.get("prun_port", 5000)
        self.working_path = os.environ["working_path"]
        self.log_path = self.get_log_path()

    def get_log_path(self):
        log_path = os.path.join(self.working_path, "log")
        if os.path.exists(log_path) is False:
            os.mkdir(log_path)
        return log_path

    def get_orig_logs(self):
        self.orig_log_folders = os.path.join(self.log_path, "org_logs_{}.yaml".format(self.prun_port))
        orig_log_folders = os.listdir(self.log_path)
        with open(self.orig_log_folders, 'w') as f:
            yaml.dump(orig_log_folders, f)

    def get_new_log(self):
        latest_log_folders = os.listdir(self.log_path)
        orig_log_folders = self.read_orig_logs()
        new_logs = []
        for item in latest_log_folders:
            if item not in orig_log_folders:
                item_path = os.path.join(self.log_path, item)
                if os.path.isdir(item_path):
                    for temp_log in os.listdir(item_path):
                        temp_log_path = os.path.join(item_path, temp_log)
                        if os.path.isfile(temp_log_path):
                            new_logs.append(temp_log_path)
        return new_logs

    def read_orig_logs(self):
        with open(self.orig_log_folders) as f:
            log_folders = yaml.load(f.read(), Loader=yaml.SafeLoader)
        return log_folders

    def save_msg(self, msg, test_case):
        test_function = test_case.split(".")
        log_file = "{}_{}.log".format(test_function[-1], time.time())
        log_path = os.path.join(self.log_path, log_file)
        with open(log_path, "w") as file_:
            file_.write(msg)
        return log_path

    def command_run_test(self, test_case, test_path):
        test_function = test_case.split(".")
        xml_name = "nosetests_%s_%s.xml" % (test_function[-1], time.time())
        xml_path = os.path.join(self.log_path, xml_name)
        command_line = "nosetests --exe --nocapture --with-printlog --with-xunit --xunit-file={} -x {}" \
            .format(xml_path, test_path)
        child1 = subprocess.Popen(command_line, shell=True)
        return_code = child1.wait()
        ret = True if return_code == 0 else False
        return ret, xml_path

    def run(self, test_case, test_path, parameters, queue):
        self.get_orig_logs()
        ret, xml_path = self.command_run_test(test_case, test_path)
        logs = self.get_new_log()
        if ret is True:
            log.INFO("TestCase run succeed.%s", test_case)
            result = State.PASS
        else:
            log.ERR("TestCase run failed. %s", test_case)
            result = State.FAIL
        result = {"name": test_case, "result": result, "log": logs, "xml_path": xml_path}
        queue.put(result)
        return ret
