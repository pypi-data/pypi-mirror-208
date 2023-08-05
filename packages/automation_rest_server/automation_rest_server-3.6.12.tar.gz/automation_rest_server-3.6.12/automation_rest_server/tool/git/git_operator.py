import subprocess
import os
import re
import platform
from utils.message import Message
from utils.system import get_ip_address, decorate_exception
from utils import log


class GitOperator(object):

    def __init__(self, user="", key="", work_path=None):
        self.root_path = os.environ["working_path"] if work_path is None else work_path
        self.user = user
        self.key = key
        self.commit = ""
        self.message = Message("Update git operation logs on {}".format(get_ip_address()))

    def _execute_git_command(self, cmd):

        if "windows" in platform.system().lower():
            new_command_line = "cd /d {} && {}".format(self.root_path, cmd)
        else:
            new_command_line = "cd {} && {}".format(self.root_path, cmd)
        log.INFO(new_command_line)
        process = subprocess.Popen(new_command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (std_output, std_error) = process.communicate()
        ret = process.poll()
        self.message.add_message("Execute: {}\n{}\n{}".
                                 format(cmd, std_output.decode("utf-8", "ignore"), std_error.decode("utf-8", "ignore")))
        return std_output, ret

    def hard_reset(self):
        cmd = "git reset --hard"
        std_output, ret = self._execute_git_command(cmd)
        return std_output, ret

    def get_project_remote_url(self):
        cmd = "git remote -v"
        std_output, ret = self._execute_git_command(cmd)
        links = re.findall("(http.*?)\s", std_output.decode("utf-8", "ignore"))
        link = links[0] if links else ""
        log.INFO("fGet url: {link}")
        return link

    def adjust_remote_url(self, orginal_url):
        new_url = orginal_url
        if "@" in orginal_url:
            temps = orginal_url.split("@")
            new_url = "https://"+temps[1]
            self.git_config_remote_url(new_url)
        return new_url

    def git_config_remote_url(self, remote_url):
        command = "git config remote.origin.url {}".format(remote_url)
        self._execute_git_command(command)

    def update_code(self, target_version):
        ret = -1
        remote_url = self.get_project_remote_url()
        remote_url = self.adjust_remote_url(remote_url)
        if remote_url != "":
            authentication = "//{}:{}@".format(self.user, self.key)
            remote_url = remote_url.replace("//", authentication)
            self.rev_parse()
            ret = self.fetch_code(remote_url)
            if ret == 0:
                commit_id = self.get_target_commit_id(target_version)
                if commit_id != "":
                    ret = self.git_check_out(commit_id)
        return ret

    def clone(self, remote_url, target_version=None):
        authentication = "//{}:{}@".format(self.user, self.key)
        remote_url = remote_url.replace("//", authentication)
        command_line = "git clone {}".format(remote_url)
        _, ret = self._execute_git_command(command_line)
        if ret == 0 and target_version is not None:
            self.root_path = os.path.join(self.root_path, self.get_url_folder(remote_url))
            commit_id = self.get_target_commit_id(target_version)
            if commit_id != b"":
                ret = self.git_check_out(commit_id)
            else:
                ret = -1
        return ret

    def rev_parse(self):
        command_line = "git rev-parse --is-inside-work-tree"
        self._execute_git_command(command_line)

    def fetch_code(self, remote_url):
        command_line = "git fetch --progress {} +refs/heads/*:refs/remotes/origin/*".format(remote_url)
        _, ret = self._execute_git_command(command_line)
        return ret

    def git_check_out(self, commit_id):
        self.commit = commit_id
        command_line = "git checkout -f {}".format(commit_id)
        _, ret = self._execute_git_command(command_line)
        return ret

    def get_target_commit_id(self, target_version):
        command_line = "git rev-parse {}".format(target_version)
        std_output, ret = self._execute_git_command(command_line)
        commit_id = std_output[0:8] if ret == 0 else b""
        return commit_id.decode("utf-8")

    def update_latest_code(self, target_version):
        try:
            _, ret = self.hard_reset()
            print("hard reset", ret)
            if ret == 0:
                self.message.add_message("Git hard reset succeed")
                ret = self.update_code(target_version)
            else:
                self.message.add_message("Git hard reset Failed, skip update code ")
        except Exception as e:
            ret = -1
            self.message.add_message("git update code failed\n{}\n".format(e))
        new_msg = re.sub("\n+", "\n", self.message.message)
        return new_msg, ret

    @staticmethod
    def get_url_folder(url):
        rets = re.findall("/(\w*)\.git", url)
        if rets:
            folder_name = rets[0]
        else:
            folder_name = ""
        return folder_name

    @decorate_exception
    def get_current_commit(self):
        commit = ""
        cmd = "git log -1"
        output, code = self._execute_git_command(cmd)
        if code == 0:
            rets = re.findall("commit\s+(\w{6})", output.decode('utf-8'))
            if rets:
                commit = rets[0]
        return commit


if __name__ == '__main__':
    a = GitOperator("shaobin.shu", "Cnex!2024", r"C:\cshu\test-platform2.0")
    a.update_latest_code("origin/main")
