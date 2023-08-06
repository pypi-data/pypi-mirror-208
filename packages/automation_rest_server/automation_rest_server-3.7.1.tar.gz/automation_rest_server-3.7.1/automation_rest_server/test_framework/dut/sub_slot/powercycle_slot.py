import os
import re
import platform
from utils import log
from utils.ssh import SSH
from utils.system import get_vendor_name
from test_framework.state import SlotState


class PowercycleSlot(object):

    def __init__(self):
        super().__init__()
        self.ssh = None
        self.cntid = None
        self.nsid = None
        self.slot = None
        self.char_dev = None
        self.block_dev = None

    def refresh(self, config):
        self.ssh_connect(config)
        if self.ssh is None:
            log.WARN("Unable to connect Linux")
        else:
            self.find_device(config)
            dev_info = self.get_info()
            slot_info = self._format_results(dev_info)
            log.INFO("refresh powercycle device %s", slot_info)
            return slot_info

    def ssh_connect(self, config):
        target_ip = config["target_ip"] if "target_ip" in config.keys() else None
        if target_ip is None:
            log.WARN("Get no target ip info")
        else:
            user = config.get('user', 'root')
            password = config.get('password', 'nvme')

            self.ssh = SSH(target_ip, username=user, password=password)
            self.ssh.open()

    def find_device(self, config):
        slot = config["slot"] if "slot" in config.keys() else None
        base_path = '/sys/class/nvme'
        _, output = self.ssh.command("ls {}".format(base_path), cmdline=False, console=False)
        for c in output.split():
            try:
                char_path = base_path + "/" + c
                _, output = self.ssh.command("cat {}/device/uevent".format(char_path), cmdline=False, console=False)
                match = re.findall(r'PCI_SLOT_NAME=([0-9a-fA-F:.]+)', output)
                if match:
                    _slot = match[0]
                    if slot is None or slot in _slot:
                        self.slot = _slot
                        self.char_dev = "/dev/" + c
                        _, output = self.ssh.command("cat {}/cntlid".format(char_path, c), cmdline=False, console=False)
                        self.cntid = int(output.strip()) if output else None
                        _, output = self.ssh.command("ls {}".format(char_path), cmdline=False, console=False)
                        match = re.findall(r'nvme\d+[c\d]*n\d+', output)
                        if match:
                            block = match[0]
                            self.block_dev = re.sub(r'c\d+', '', block)
                            _, output = self.ssh.command("cat {}/{}/nsid".format(char_path, block), cmdline=False, console=False)
                            self.nsid = int(output.strip()) if output else None
                            break

            except Exception:
                pass

        if self.nsid is None:
            raise AssertionError('Cannot find device by slot {}'.format(slot))
        else:
            log.INFO('char: %s, block: %s, cntid: %d, nsid: %d', self.char_dev, self.block_dev, self.cntid, self.nsid)


    def get_info(self):
        dev_info = {}
        ssd_config_dic = self.get_ssd_config_info()
        drive_life_info_dic = self.get_drive_life_info_info()
        test_fw_config_dic = self.get_test_fw_config_info()
        dev_info['ssd_config_dic'] = ssd_config_dic
        dev_info['drive_life_info_dic'] = drive_life_info_dic
        dev_info['test_fw_config_dic'] = test_fw_config_dic
        return dev_info

    def get_ssd_config_info(self):
        ssd_config_dic = {}
        output = self.get_id_ctrl_info()
        tnvmecap = self.check_data(int(re.findall(r'tnvmcap\s+:(.+)\n', output)[0].strip()))
        vid = self.check_data(int(re.findall(r'vid\s+:(.+)\n', output)[0].strip(), 16))
        drive_sn = self.check_data(re.findall(r'sn\s+:(.+)\n', output)[0].strip())
        drive_pn = self.check_data(re.findall(r'mn\s+:(.+)\n', output)[0].strip())
        output = self.get_drive_security_info()
        security_type = "ISE" if int(re.findall(r'0000: .. .. (\w+) ', output)[0], 16) else "SED"
        security_status = "security enable" if int(re.findall(r'0000: .. .. .. (\w+) ', output)[0], 16) else "security disable"
        output = self.get_int_type_info()
        int_type = self.check_data(re.findall(r'"(\w+)', output)[0])

        ssd_config_dic['drive_sn'] = drive_sn
        ssd_config_dic['drive_pn'] = drive_pn
        ssd_config_dic['vid'] = vid
        ssd_config_dic['drive_tnvmcap'] = tnvmecap
        ssd_config_dic['security_status'] = security_status
        ssd_config_dic['security_type'] = security_type
        ssd_config_dic['int_type'] = int_type
        return ssd_config_dic

    def get_drive_life_info_info(self):
        drive_life_info_dic = {}
        output = self.get_drive_security_info()
        life_cycle_state = self.get_sum(re.findall(r'0010: (\w+) (\w+) (\w+) (\w+) ', output)[0])
        output = self.get_log_page_info()
        count_grown_defects = self.get_sum(re.findall(r'0090: (\w+) (\w+) (\w+) (\w+) ', output)[0])
        count_primary_defects = self.get_sum(re.findall(r'0090: .. .. .. .. .. .. .. .. (\w+) (\w+) (\w+) (\w+) ', output)[0])
        nand_max_erase_count = self.get_sum(re.findall(r'0070: (\w+) (\w+) ', output)[0])
        nand_min_erase_count = self.get_sum(re.findall(r'0060: (\w+) (\w+) ', output)[0])
        nand_avg_erase_count = self.get_sum(re.findall(r'0060: .. .. .. .. .. .. .. .. (\w+) (\w+) ', output)[0])

        drive_life_info_dic['life_cycle_state'] = life_cycle_state
        drive_life_info_dic['count_grown_defects'] = count_grown_defects
        drive_life_info_dic['count_primary_defects'] = count_primary_defects
        drive_life_info_dic['nand_max_erase_count'] = nand_max_erase_count
        drive_life_info_dic['nand_min_erase_count'] = nand_min_erase_count
        drive_life_info_dic['nand_avg_erase_count'] = nand_avg_erase_count
        return drive_life_info_dic

    def get_test_fw_config_info(self):
        test_fw_config_dic = {}
        output = self.get_id_ctrl_info()
        match = re.findall(r'00[0123]+: [\w\s]+ "(.+)"', output)
        fw_repo = self.check_data(''.join(match).strip("."))
        fw_branch_name = self.check_data(re.findall(r'0100: [\w\s]+ "(.+)"', output)[0].strip('.'))
        fw_private_revision = self.check_data(re.findall('commit.(\w+)', output)[0])
        fw_public_revision = self.check_data(re.findall(r'fr\s+:(.+)\n', output)[0].strip())

        test_fw_config_dic['fw_public_revision'] = fw_public_revision
        test_fw_config_dic['fw_repo'] = fw_repo
        test_fw_config_dic['fw_private_revision'] = fw_private_revision
        test_fw_config_dic['fw_branch_name'] = fw_branch_name
        return test_fw_config_dic

    def get_id_ctrl_info(self):
        cmd = "nvme id-ctrl {} -v".format(self.char_dev)
        _, output = self.ssh.command(cmd, cmdline=False, console=False)
        return output

    def get_drive_security_info(self):
        cmd = "nvme admin-passthru {} -o 0xc0 -l 0x20 -4 0x1000204f -5 0x4 -r".format(self.char_dev)
        _, output = self.ssh.command(cmd, cmdline=False, console=False)
        return output

    def get_int_type_info(self):
        cmd = "nvme admin-passthru {} -o 0xc0 -l 0x10  -4 0x10002034 -5 0x4 -r".format(self.char_dev)
        _, output = self.ssh.command(cmd, cmdline=False, console=False)
        return output

    def get_log_page_info(self):
        cmd = "	nvme get-log {} -i 0xde -l 512 -s 0".format(self.char_dev)
        _, output = self.ssh.command(cmd, cmdline=False, console=False)
        return output

    def get_sum(self, match):
        sum = 0
        for i, item in enumerate(match):
            sum += int(item, 16) << (i*8)
        return sum

    def check_data(self, val):
        if val:
            return val
        return ""

    def _format_results(self, results):
        format_result = {
            "vendor": get_vendor_name(results["ssd_config_dic"]["vid"]),
            "fw_version": results["test_fw_config_dic"]["fw_public_revision"],
            "commit": results["test_fw_config_dic"]["fw_private_revision"][0:6],
            "ise/sed": results["ssd_config_dic"]["security_type"],
            "sn": results["ssd_config_dic"]["drive_sn"],
            "cap": self.convert_t(results["ssd_config_dic"]["drive_tnvmcap"]),
            "bb": results["drive_life_info_dic"]["count_grown_defects"],
            "max_ec": results["drive_life_info_dic"]["nand_max_erase_count"],
            "avg_ec": results["drive_life_info_dic"]["nand_avg_erase_count"],
            "status": SlotState.Idle
        }
        return format_result

    @staticmethod
    def convert_t(cap):
        return float('%.2f' % (cap/1000/1000/1000/1000))
