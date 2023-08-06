import os
import json
import subprocess
import sys


class PIPOperation(object):

    def __init__(self):
        pass

    @staticmethod
    def print_update_info(package):
        print("{} current version {}, have new version {}\nPlease update with command:\npip3 install -U {}".
              format(package["name"], package["version"], package["latest_version"], package["name"]))

    def have_new_version(self, name="automation-rest-server"):
        self.upgrade_pip()
        result = self.check_new_version(name)
        return result

    @staticmethod
    def check_new_version(name):
        result = False
        command_line = "pip list --outdated --format=json --not-required"
        print("Checking new version of prun.")
        process = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (std_output, std_error) = process.communicate()
        ret = process.poll()
        if ret == 0:
            update_packages = json.loads(std_output.decode("utf-8"))
            finds = [item for item in update_packages if item["name"] == name]
            if finds:
                PIPOperation.print_update_info(finds[0])
            result = True if finds else False
        return result

    @staticmethod
    def upgrade_pip():
        if "win" in sys.platform:
            cmd = "python.exe -m pip install --upgrade pip"
            os.system(cmd)

    @staticmethod
    def upgrade_prun():
        print("Begin to upgrade prun")
        command_line = "pip3 install -U automation_rest_server"
        os.system(command_line)

    def check_version(self):
        if self.have_new_version():
            self.upgrade_prun()
