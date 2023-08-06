# coding=utf-8
import time
import os
from multiprocessing import Queue
from utils import log
from utils.process import MyProcess
from test_framework.engine import PersesEngine, OakgateEngine, PersesPowerEngine, NoseEngine, SSEEngine
from utils.system import decorate_exception
from tool.git.git_operator import GitOperator
from test_framework.engine.special_parameter import Parameters


class Runner(object):

    def __init__(self):
        self.results = list()
        self.process_run_ = None
        self.working_path = os.environ["working_path"]
        self.engine = self.get_engine()
        # self.log_path = self.get_log_path()

    def get_engine(self):
        if "test-platform" in self.working_path:
            engine = OakgateEngine()
        elif self.is_perses_power_cycle() is True:
            engine = PersesPowerEngine()
        elif "perses" in self.working_path:
            engine = PersesEngine()
        elif "neuron" in self.working_path:
            engine = SSEEngine()
        elif "venus" in self.working_path:
            engine = NoseEngine()
        else:
            raise AssertionError('Prun start on wrong path: {}'.format(self.working_path))
        print("get engine", engine)
        return engine

    def get_results(self):
        return self.results

    def is_perses_power_cycle(self):
        result = False
        if ("perses_power_cycle" in os.environ.keys()) and ("perses" in self.working_path.lower()):
            result = True
        return result

    def stop(self):
        print("test runner . stop")
        if self.process_run_ is not None:
            ret = self.process_run_.stop()
        else:
            ret = -1
        return ret

    @staticmethod
    def update_git(parameters):
        if "git_version" in parameters.keys():
            git_version = parameters["git_version"]
            user = parameters["git_user"]
            passwd = parameters["git_key"]
            log.INFO(f"Git update: user: {user}, version: {git_version}")
            git = GitOperator(user, passwd)
            msg, ret = git.update_latest_code(git_version)
            log.INFO(f"Git update result:  {ret}, msg: {msg}")

    @staticmethod
    def pop_git_parameters(parameters):
        para = Parameters()
        parameters = para.pop_parm(parameters, "git_user")
        parameters = para.pop_parm(parameters, "git_key")
        parameters = para.pop_parm(parameters, "git_version")
        return parameters

    @decorate_exception
    def process_run(self, test_case, test_case_path=None, parameters=None, loop=1, timeout=0):
        log.INFO("process_run")
        value = None
        git = GitOperator()
        self.update_git(parameters)
        parameters = self.pop_git_parameters(parameters)
        for item in range(loop):
            log.INFO("Run test in loop: %s", item)
            start_time = time.time()
            current_time = start_time
            queue = Queue()
            print(test_case, test_case_path, parameters)
            self.process_run_ = MyProcess(target=self.engine.run, args=(test_case, test_case_path, parameters, queue,))
            self.process_run_.daemon = True
            self.process_run_.start()
            if timeout > 0:
                while current_time - start_time < timeout:
                    current_time = time.time()
                    time.sleep(5)
                self.process_run_.stop()
            else:
                self.process_run_.join()
            value = queue.get(True)
            commit = git.get_current_commit()
            value["commit"] = commit
            self.results.append(value)
        return value
