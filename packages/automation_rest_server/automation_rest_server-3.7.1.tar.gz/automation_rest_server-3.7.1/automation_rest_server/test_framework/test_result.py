# coding=utf-8
import os
import  xml.dom.minidom
from utils.system import get_ip_address


class TestResult(object):

    def __init__(self):
        pass

    def _get_log_txt(self, log_path):
        msg = "Log path: {}".format(log_path)
        if os.path.exists(log_path):
            file_size = os.path.getsize(log_path)
            if file_size > 100*1024*1024:
                txt_ = "Log file more than 100M, please check it on test environment: {}".format(log_path)
            else:
                txt_ = self.read_log(log_path)
        else:
            txt_ = "Log file not exists: {}".format(log_path)
        msg = "{} \n{}".format(msg, txt_)
        return msg

    @staticmethod
    def read_log(log_path):
        file_ = open(log_path, encoding='utf-8')
        lines_ = file_.readlines()
        numbers = len(lines_)
        if numbers > 5000:
            new_lines = lines_[0:500]
            new_lines.append("............\n............\n............\n")
            end_lines = lines_[-1000:]
            new_lines.extend(end_lines)
        else:
            new_lines = lines_
        logs = ''.join(new_lines)
        file_.close()
        return logs

    def get_xml_report_txt(self, xml_path):
        log_path_print = "Log at: {} \n".format(xml_path)
        dom = xml.dom.minidom.parse(xml_path)
        root = dom.documentElement
        system_out_element = root.getElementsByTagName('system-out')
        system_out_tex = system_out_element[0].firstChild.wholeText if system_out_element else ""
        fail_element = root.getElementsByTagName('failure')
        fail_txt = fail_element[0].firstChild.wholeText if fail_element else ""
        error_element = root.getElementsByTagName('error')
        error_txt = error_element[0].firstChild.wholeText if error_element else ""
        sys_error_element = root.getElementsByTagName('system-err')
        sys_error_txt = sys_error_element[0].firstChild.wholeText if sys_error_element else ""
        xml_logs = log_path_print + system_out_tex + fail_txt + error_txt + sys_error_txt

        return xml_logs

    def get_log(self, logs):
        log = str()
        try:
            if type(logs) is list:
                for item in logs:
                    log_content = self._get_log_txt(item)
                    log = "{}\n{}\n{}".format(log, item, log_content)
            else:
                log = self._get_log_txt(logs)
        except Exception as all_exception:
            print(all_exception)
        return log

    @staticmethod
    def generate_msg_head(log_name):
        head = "\n"+"*"*100+"\n"+"*"*15+log_name+"*"*15+"\n"+"*"*100+"\n"
        return head

    def get_test_suite_test_msg(self, test_results):
        print("get_test_suite_test_msg")
        print(test_results)
        msg = ""
        if type(test_results) is list:
            for test_result in test_results:
                if "xml_path" in test_result.keys():
                    xml_log = self.get_xml_logs(test_result["xml_path"])
                    msg = msg + self.generate_msg_head(test_result["xml_path"]) + xml_log + "\n"
                if "msg" in test_result.keys():
                    msg = msg + self.generate_msg_head("") + str(test_result["msg"])
                if "log" in test_result.keys():
                    logs = test_result["log"]
                    msg = msg + self.generate_msg_head("Logs information") + str(self.get_log(logs))
        elif type(test_results) is str:
            msg = test_results
        return msg

    @staticmethod
    def check_file_size(path):
        result = False
        if os.path.exists(path):
            file_size = os.path.getsize(path)
            result = True if file_size < 10*1024*1024 else False
        return result

    def get_xml_logs(self, log_path):
        if os.path.exists(log_path):
            if self.check_file_size(log_path):
                xml_log = self.get_xml_report_txt(log_path)
            else:
                xml_log = "log file more than 10M, do not upload file.\n" \
                          "logs at host: {}, path: {}".format(get_ip_address(), log_path)
        else:
            xml_log = "log file not exist, test abnormal end, it may test case script issue, please check test case\n" \
                      "logs at host: {}, path: {}".format(get_ip_address(), log_path)
        return xml_log
