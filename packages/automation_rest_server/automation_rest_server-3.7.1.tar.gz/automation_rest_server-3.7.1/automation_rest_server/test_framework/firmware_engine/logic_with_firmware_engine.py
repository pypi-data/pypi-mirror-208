
import os
import time
import shutil
import ftplib
from tool.git.git_operator import GitOperator
from utils.ssh import SSH
from utils.system import decorate_exception_result
from utils.serial_tool import CnexSerial
from utils import log


class LogicFWDownloader(object):

    def __init__(self):
        self.ic_ftp = "172.29.0.208"
        self.ic_ftp_user = "lab"
        self.ic_ftp_pwd = "lab"
        self.ftp_patten = "fpga.7z"
        self.local_ftp_path = r"C:\prun"
        self.local_ftp_fpga_path = os.path.join(self.local_ftp_path, "fpga")
        self.local_fw_path = os.path.join(self.local_ftp_path, "firmware")
        self.git_url = "https://git.cnexlabs.com/cnex-firmware/tahoe_fw.git"
        self.local_fw_pj_path = self.get_git_project_path()
        self.init_local_folder()

    def init_local_folder(self):
        init_path = [self.local_ftp_path, self.local_ftp_fpga_path, self.local_fw_path]
        for temp_path in init_path:
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)

    @staticmethod
    def is_directory(ftp, path):
        try:
            ftp.cwd(path)
            return True
        except ftplib.error_perm:
            return False

    @staticmethod
    def unzip_fpga_file(zip_path):
        import py7zr
        with py7zr.SevenZipFile(zip_path, mode="r") as z:
            z.extractall(path=os.path.dirname(zip_path))
        unzip_folder = os.path.splitext(os.path.basename(zip_path))[0]
        unzip_folder_path = os.path.join(os.path.dirname(zip_path), unzip_folder)
        for temp in os.listdir(unzip_folder_path):
            if temp.endswith(".sof"):
                return os.path.join(unzip_folder_path, temp)

    def ftp_download_file(self, ftp, fpga_folder, fpga_file):
        local_path = os.path.join(self.local_ftp_fpga_path, fpga_folder)
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
        os.mkdir(local_path)
        local_fpga_file = os.path.join(local_path, fpga_file)
        with open(local_fpga_file, 'wb') as f:
            ftp.retrbinary(f'RETR {fpga_file}', f.write)
        return local_fpga_file

    def _get_file_name(self, ftp):
        fpga_file = None
        filenames = ftp.nlst()
        for file_ in filenames:
            if self.ftp_patten in file_:
                fpga_file = file_
                break
        return fpga_file

    def split_path_folder_file(self, ftp, ftp_path):
        ftp_path = ftp_path.replace(f"ftp://{self.ic_ftp}/", "")
        split_paths = ftp_path.split("/")
        if not self.is_directory(ftp, ftp_path):
            fpga_file = split_paths[-1]
            fpga_folder = split_paths[-2]
            ftp.cwd(os.path.dirname(ftp_path))
        else:
            fpga_folder = split_paths[-1] if split_paths[-1] != "" else split_paths[-2]
            fpga_file = self._get_file_name(ftp)
        return fpga_folder, fpga_file

    def get_fpga_from_ftp(self, ftp_path):
        log.INFO(f"Begin to get sof from {ftp_path}")
        ftp = ftplib.FTP(self.ic_ftp, self.ic_ftp_user, self.ic_ftp_pwd)
        fpga_folder, fpga_file = self.split_path_folder_file(ftp, ftp_path)
        dl_fpga_path = self.ftp_download_file(ftp, fpga_folder, fpga_file)
        sof_file = self.unzip_fpga_file(dl_fpga_path)
        log.INFO(f"Get sof {sof_file} from ftp")
        ftp.quit()
        if sof_file is None:
            raise RuntimeError(f"sof_file get failed: {ftp_path}")
        return sof_file

    def get_git_project_path(self):
        basename = os.path.basename(self.git_url)
        folder_name = os.path.splitext(basename)[0]
        return os.path.join(self.local_fw_path, folder_name)

    def update_fw_code(self, branch):
        local_fw_path = self.local_fw_pj_path if os.path.exists(self.local_fw_pj_path) else self.local_fw_path
        git = GitOperator("shaobin.shu", "Cnex!2024", local_fw_path)
        if os.path.exists(self.local_fw_pj_path):
            new_msg, ret = git.update_latest_code(f"origin/{branch}")
            if ret != 0:
                raise RuntimeError(f"Git update failed, url:{self.git_url} branch:{branch}")
        else:
            if git.clone(self.git_url, f"origin/{branch}") != 0:
                raise RuntimeError(f"Git clone failed, url:{self.git_url} branch:{branch}")

    def copy_sof_2_fw(self, src_sof):
        dst_sof = os.path.join(self.local_fw_pj_path, "tahoe.sof")
        if os.path.exists(dst_sof):
            os.remove(dst_sof)
        shutil.copy(src_sof, dst_sof)

    def load_all(self):
        cmd = f"cd /d {self.local_fw_pj_path} && load_all.bat"
        log.INFO(f"upgrade logic and firmware with cmd: {cmd}")
        ret = os.system(cmd)
        if ret != 0:
            raise RuntimeError("load_all failed")
        time.sleep(60)

    def insmod_ko(self, ssh, venus):
        ko_path = f"{venus}/bin/tahoe/qa_mode"
        cmd = f"cd {ko_path} && insmod nexus.ko && insmod ktest.ko"
        status, output = ssh.command(cmd)
        if status != 0:
            raise RuntimeError(f"insmod failed, cmd: {cmd}. Output:{output}")

    def reboot_linux(self, linux, user, pwd, venus_path):
        ssh = SSH(linux, username=user, password=pwd)
        ssh.open()
        ssh.command_without_result("reboot -nf", timeout=10)
        time.sleep(60)
        ssh.open()
        self.insmod_ko(ssh, venus_path)

    @staticmethod
    def clear_uart(com):
        ser = CnexSerial(com)
        ser.close_ttermpro()
        time.sleep(2)
        ser.clearspi1()
        time.sleep(2)
        ser.open_ttermpro()

    @decorate_exception_result
    def run(self, para):
        log.INFO("Begin to download logic and firmware")
        src_sof = self.get_fpga_from_ftp(para["ic_logic"])
        self.update_fw_code(para["ic_fw_branch"])
        self.clear_uart(para["com"])
        self.copy_sof_2_fw(src_sof)
        self.load_all()
        self.reboot_linux(para["target_ip"], para["linux_user"], para["linux_pwd"], para["work_path"])
        return 0, "download logic and firmware succeed"
