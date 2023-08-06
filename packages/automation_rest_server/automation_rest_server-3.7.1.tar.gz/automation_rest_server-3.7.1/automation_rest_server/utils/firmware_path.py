
import os
import platform
import sys
from utils import log


class FirmwareBinPath(object):

    def __init__(self):
        self.linux_path = "/home/share/release"
        self.windows_path = r"\\172.29.190.4\share\release"
        self.auto_build_folder = "nightly"

    def get_default_base_path(self):
        if "win" in sys.platform.lower():
            base_path = self.windows_path
        else:
            base_path = self.linux_path
        return base_path

    def get_image_path(self, base_path, commit_id, nand):
        if os.path.exists(base_path):
            commit_6bit = commit_id[0:6]
            nand = nand.lower()
            _files = os.listdir(base_path)
            for item in _files:
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path) and commit_6bit in item:
                    ret = self.get_image_path(item_path, commit_id, nand)
                    if ret is not None:
                        return ret
                elif "preBootloader".lower() not in item.lower() and item.endswith(".bin") and \
                        "{}".format(nand) in item.lower():
                    return os.path.join(base_path, item)

    @staticmethod
    def get_cap(parameters):
        base_path = parameters.get("fw_path", "")
        nand = parameters.get("nand", "RV04")
        dir_path = os.path.dirname(base_path) if os.path.isfile(base_path) else base_path
        for item in os.listdir(dir_path):
            if nand in item and item.endswith(".cap"):
                return os.path.join(dir_path, item)

    def get_fw_path_from_parameter(self, parameters, base_path=""):
        nand = parameters.get("nand", "BICS5")
        commit = parameters.get("commit", "")
        fw_path = parameters.get("fw_path", base_path) if base_path == "" else base_path
        if not os.path.isfile(fw_path):
            log.INFO("fw path {} commit {} nand {}".format(fw_path, commit, nand))
            fw_path = self.get_image_path(fw_path, commit, nand)
        log.INFO("Get path from parameters: {}".format(fw_path))
        return fw_path

    @staticmethod
    def get_spi_path(parameters):
        spi = None
        fw_path = parameters.get("fw_path", "")
        if os.path.exists(fw_path):
            dir_path = os.path.dirname(fw_path) if os.path.isfile(fw_path) else fw_path
            files = [
                os.path.join(dir_path, item) for item in os.listdir(dir_path)
                if "_SPIAPP_" in item and item.endswith(".cap")
            ]
            if len(files) == 0:
                log.ERR(f"can not find _SPIAPP_ file in directory: {dir_path}")
            else:
                spi = files[0]
        return spi

    @staticmethod
    def change_path_win_2_linux(win_path):
        if win_path is not None:
            path_temp = win_path.replace("\\\\172.29.190.4", "/home")
            linux_path = path_temp.replace("\\", "/")
            log.INFO("Get linux path: {}".format(linux_path))
        else:
            linux_path = "not_find_linux_path"
        return linux_path

    @staticmethod
    def change_path_linux_2_win(linux_path):
        if linux_path is not None:
            linux_path = linux_path.replace("//", "/")
            path_temp = linux_path.replace("/home", "\\\\172.29.190.4")
            win_path = path_temp.replace("/", "\\")
            log.INFO("Get win path: {}".format(win_path))
        else:
            win_path = "not_find_win_path"
        return win_path

    def get_default_base_path_enhance(self, parameters):
        if "base_path" in parameters.keys():  # for oakgate
            return parameters["base_path"]
        if "fw_path" in parameters.keys():   # for perses
            temp_path = parameters["fw_path"]
            if "172.29.190.4" in temp_path:
                if "win" in sys.platform.lower():
                    base_path = temp_path
                else:
                    base_path = self.change_path_win_2_linux(temp_path)
            else:
                base_path = temp_path
        else:
            base_path = self.get_default_base_path()
        log.INFO("Get base path: {}".format(base_path))
        return base_path

    def generate_oakgate_images(self, parameters):
        output_parm = dict()
        nand = parameters.get("nand", "ALL")
        for image_key in ["base_image", "target_image"]:
            if image_key in parameters:
                image_path = parameters.get(image_key)
                if os.path.isdir(image_path):
                    ret = self.get_image_path(image_path, "", nand)
                    if ret is not None:
                        output_parm[image_key] = ret
        return output_parm

    def update_perses_fw_path(self, parameters):
        if "fw_path" in parameters.keys():
            if "win" in platform.system().lower():
                temp_path = self.change_path_linux_2_win(parameters["fw_path"])
            else:
                temp_path = self.change_path_win_2_linux(parameters["fw_path"])
        else:
            temp_path = self.get_default_base_path_enhance(parameters)
        fw_path = self.get_fw_path_from_parameter(parameters, temp_path)
        if fw_path is not None:
            log.INFO("update_perses_fw_path: {}".format(fw_path))
            parameters["fw_path"] = fw_path
            os.environ["fw_path"] = fw_path
        else:
            log.WARN("Not find path: perses_fw_path")
        print(parameters)
        return parameters
