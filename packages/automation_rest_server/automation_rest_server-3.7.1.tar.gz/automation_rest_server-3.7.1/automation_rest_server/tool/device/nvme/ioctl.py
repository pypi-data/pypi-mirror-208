#!/usr/bin/env python
# pylint: disable=too-many-locals,too-many-arguments,superfluous-parens,invalid-name,keyword-arg-before-vararg
"""
Created on 2019/4/26

@author: yyang
"""
import re
import fcntl
import math
import os
import random
from ctypes import memmove, sizeof, addressof
from tool.device.nvme.struct import *
from utils import log


def _iowr(_tp, _nr, _sz):
    return (3 << 30) + (sizeof(_sz) << 16) + (ord(_tp) << 8) + _nr


def _iow(_tp, _nr, _sz):
    return (1 << 30) + (sizeof(_sz) << 16) + (ord(_tp) << 8) + _nr


def _io(_tp, _nr):
    return (ord(_tp) << 8) + _nr


class DEVICE:

    def __init__(self, cntid=0, nsid=1, slot=None):
        self._cntid = cntid
        self._nsid = nsid
        self._slot = slot

        self._c_dev = None
        self._b_dev = None
        self._s_dev = None
        self._devices = []

    def scan_devices(self):
        self._scan_devices()

        if self._slot:
            self._get_device_by_slot()
        else:
            self._get_device_by_cntid_nsid()

    @property
    def nsid(self):
        return self._nsid

    @property
    def cntid(self):
        return self._cntid

    @property
    def char(self):
        return self._c_dev

    @char.setter
    def char(self, name):
        self._c_dev = name

    @property
    def block(self):
        return self._b_dev

    @property
    def slot(self):
        return self._s_dev

    @property
    def all_devices(self):
        return self._devices

    def _get_device_by_cntid_nsid(self):
        for device in self._devices:
            if device['cntid'] == self._cntid:
                self._s_dev = device['slot']
                self._c_dev = '/dev/' + device['char']
                for node in device['nodes']:
                    if node['nsid'] == self._nsid:
                        self._b_dev = '/dev/' + node['block']
                return
        raise AssertionError('Cannot find device by cntid {} nsid {}'.format(self._cntid, self._nsid))

    def _get_device_by_slot(self):
        for device in self._devices:
            if self._slot in device['slot']:
                self._s_dev = device['slot']
                self._cntid = device['cntid']
                self._c_dev = '/dev/' + device['char']
                for node in device['nodes']:
                    if node['nsid'] == self._nsid:
                        self._b_dev = '/dev/' + node['block']
                        break
                return
        raise AssertionError('Cannot find device by slot {}'.format(self._slot))

    def _scan_devices(self):
        base_path = '/sys/class/nvme'
        for c in os.listdir(base_path):
            try:
                _cntlid = os.path.join(base_path, c, 'cntlid')
                if os.path.exists(_cntlid):
                    with open(_cntlid) as cntlid_f:
                        cntid = int(cntlid_f.read().strip())
                else:
                    cntid = 0

                _slot = None
                _device = os.path.join(base_path, c, 'device', 'uevent')
                if os.path.exists(_device):
                    with open(_device) as device_f:
                        match = re.findall(r'PCI_SLOT_NAME=([0-9a-fA-F:.]+)', device_f.read())
                    if match:
                        _slot = match[0]

                device = {'cntid': cntid, 'char': c, 'slot': _slot, 'nodes': list()}

                char_path = os.path.join(base_path, c)
                for b in os.listdir(char_path):
                    if re.findall(r'nvme\d+[c\d]*n\d+', b):
                        _nsid = os.path.join(char_path, b, 'nsid')
                        if os.path.exists(_nsid):
                            with open(_nsid) as nsid_f:
                                nsid = int(nsid_f.read().strip())
                        else:
                            nsid = None
                        device['nodes'].append({'nsid': nsid, 'block': re.sub(r'c\d+', '', b)})

                self._devices.append(device)

            except Exception:
                pass

        return self._devices

class IOCTL(object):
    NVME_IOCTL_ADMIN_CMD = _iowr('N', 0x41, NVMePassthruCmd)
    NVME_IOCTL_SUBMIT_IO = _iow('N', 0x42, NVMeUserIO)
    NVME_IOCTL_IO_CMD = _iowr('N', 0x43, NVMePassthruCmd)
    NVME_IOCTL_RESET = _io('N', 0x44)
    NVME_IOCTL_SUBSYS_RESET = _io('N', 0x45)
    _instance = {}
    def __new__(cls, cntid=0, nsid=1, slot=None):

        device = DEVICE(cntid, nsid, slot)
        device.scan_devices()

        if device.block:
            dev = '{}_{}'.format(str(cls), device.block)
        else:
            # If block device is not valid, using char device and rand(0, 9999) as name
            dev = '{}_{}_{:04d}'.format(str(cls), device.char, random.randint(0, 9999))

        #if cls._instance is None:
        if dev not in cls._instance.keys():
            cls._instance[dev] = super().__new__(cls)
        return cls._instance[dev]

    def __init__(self, cntid=0, nsid=1, slot=None):
        self._c_fd = -1
        self._b_fd = -1

        self._device = DEVICE(cntid, nsid, slot)
        self._device.scan_devices()

        log.INFO('char: %s, block: %s, cntid: %d, nsid: %d', self._device.char, self._device.block, self._device.cntid, self._device.nsid)

    def __del__(self):
        self._close_c_fd()
        self._close_b_fd()

    @staticmethod
    def _get_b_dev(path, nsid=1):
        for b in os.listdir(path):
            if re.findall(r'nvme\d+[c\d]*n\d+', b):
                _nsid = os.path.join(path, b, 'nsid')
                assert os.path.exists(_nsid), 'File: {} is not exists!'.format(_nsid)
                if int(open(_nsid).read().strip()) == nsid:
                    return re.sub(r'c\d+', '', b)
        return None

    @staticmethod
    def _open(dev):
        assert os.path.exists(dev), 'Device({}) is not exists'.format(dev)
        return os.open(dev, os.O_RDWR)

    @property
    def nsid(self):
        return self._device.nsid

    @property
    def cntid(self):
        return self._device.cntid

    @property
    def block_dev(self):
        return self._device.block

    @property
    def char_dev(self):
        return self._device.char

    @property
    def slot_dev(self):
        return self._device.slot

    @property
    def char_fd(self):
        if self._c_fd == -1:
            self._c_fd = self._open(self._device.char)
        return self._c_fd

    @property
    def block_fd(self):
        if self._b_fd == -1:
            self._b_fd = self._open(self._device.block)
        return self._b_fd

    def _get_dev(self, cntid=0, nsid=0):
        """
        # 1. nsid=0, return (nvme{cntid}, nvme{cntid}n1)
        2. cntid=0, match nsid only
        3. cntid!=0, match both cntid and nsid
        4. No math, raise AssertionError
        """
        path = '/sys/class/nvme'

        return ["nvme{}".format(cntid), "nvme{}n{}".format(cntid, nsid)]
        # for c in os.listdir(path):
        #     _cntlid = os.path.join(path, c, 'cntlid')
        #
        #     # If specified cntid and cntlid file is exists, should match it.
        #     if cntid != 0 and os.path.exists(_cntlid):
        #         if int(open(_cntlid).read().strip()) != cntid:
        #             continue
        #
        #         b = self._get_b_dev(os.path.join(path, c), nsid=nsid)
        #         return c, b
        #
        #     # If cntid is not specified, only math the nsid.
        #     b = self._get_b_dev(os.path.join(path, c), nsid=nsid)
        #     if b:
        #         return c, b
        #
        # raise AssertionError('No match char device!')

    def _close_c_fd(self):
        if self._c_fd != -1:
            os.close(self._c_fd)
            self._c_fd = -1

    def _close_b_fd(self):
        if self._b_fd != -1:
            os.close(self._b_fd)
            self._b_fd = -1

    def close(self):
        self.__del__()

    def _ioctl(self, fd, request, cmd=None, status=0, timeout=None):
        if timeout and cmd:
            cmd.TIMEOUT = timeout

        _status = fcntl.ioctl(fd, request, cmd) if cmd else fcntl.ioctl(fd, request)

        try:
            assert (_status & 0x7ff) == status, "CQE Status Field Check Failed!"
        except AssertionError:
            log.DUMP('Actual Status: {:#x}, {}'.format(_status, STATUS_FIELD.get(_status & 0x7ff, 'Unknown')))
            log.DUMP("Expect Status: {:#x}, {}".format(status, STATUS_FIELD.get(status & 0x7ff, 'Unknown')))
            if cmd:
                cmd_set = OPCODE.ADMIN if request == self.NVME_IOCTL_ADMIN_CMD else OPCODE.IO
                log.DUMP('Command : {}'.format(cmd_set.get(cmd.OPCODE, 'Unknown')))
                sqe = [(f[0], '{:#x}'.format(getattr(cmd.BITS, f[0]))) for f in getattr(cmd.BITS, '_fields_')]
                log.DUMP('SQE : {}'.format(dict(sqe)))
            raise

        return _status

    def nvme_io(self, cmd, **kwargs):
        return self._ioctl(self.block_fd, self.NVME_IOCTL_SUBMIT_IO, cmd, **kwargs)

    def io_passthru(self, cmd, **kwargs):
        return self._ioctl(self.block_fd, self.NVME_IOCTL_IO_CMD, cmd, **kwargs)

    def admin_passthru(self, cmd, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_ADMIN_CMD, cmd, **kwargs)

    def reset(self, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_RESET, **kwargs)

    def subsys_reset(self, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_SUBSYS_RESET, **kwargs)

    @staticmethod
    def set_expected_status_field(status):
        assert False, 'Not support, status={:#x}!'.format(status)


class ADMIN(IOCTL):
    def abort(self, sqid, cid, **kwargs):
        cdw10 = AbortDword10()
        cdw10.SQID = sqid
        cdw10.CID = cid

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.ABORT
        cmd.CDW[10] = cdw10.DWORD

        return self.admin_passthru(cmd, **kwargs), cmd.RESULT

    def create_io_cq(self, qid, qsize, pc=1, ien=1, iv=0, **kwargs):
        cdw10 = CreateIOCQDword10()
        cdw10.QID = qid
        cdw10.QSIZE = qsize - 1

        cdw11 = CreateIOCQDword11()
        cdw11.PC = pc
        cdw11.IEN = ien
        cdw11.IV = iv

        dptr = (c_uint32 * (4 * qsize))()

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.CREATE_IO_CQ
        cmd.CDW[10] = cdw10.DWORD
        cmd.CDW[11] = cdw11.DWORD
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)

        return self.admin_passthru(cmd, **kwargs)

    def create_io_sq(self, qid, qsize, pc=1, qprio=1, cqid=0, **kwargs):
        cdw10 = CreateIOCQDword10()
        cdw10.QID = qid
        cdw10.QSIZE = qsize - 1

        cdw11 = CreateIOSQDword11()
        cdw11.PC = pc
        cdw11.QPRIO = qprio
        cdw11.CQID = cqid

        dptr = (c_uint32 * (16 * qsize))()

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.CREATE_IO_SQ
        cmd.CDW[10] = cdw10.DWORD
        cmd.CDW[11] = cdw11.DWORD
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)

        return self.admin_passthru(cmd, **kwargs)

    def delete_io_cq(self, qid, **kwargs):
        cdw10 = DeleteIOCQDword10()
        cdw10.QID = qid

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.DELETE_IO_CQ
        cmd.CDW[10] = cdw10.DWORD

        return self.admin_passthru(cmd, **kwargs)

    def delete_io_sq(self, qid, **kwargs):
        cdw10 = DeleteIOSQDword10()
        cdw10.QID = qid

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.DELETE_IO_SQ
        cmd.CDW[10] = cdw10.DWORD

        return self.admin_passthru(cmd, **kwargs)

    def device_self_test(self, stc, nsid=1, **kwargs):
        cdw10 = DeviceSelfTest()
        cdw10.STC = stc

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.DEVICE_SELF_TEST
        cmd.NSID = nsid
        cmd.CDW[10] = cdw10.DWORD

        return self.admin_passthru(cmd, **kwargs)

    def directive_send(self, dptr, doper=0, dtype=0, dspec=0, cdw12=0, nsid=1, **kwargs):
        cdw11 = DirectiveDW11()
        cdw11.DOPER = doper
        cdw11.DTYPE = dtype
        cdw11.DSPEC = dspec

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.DIRECTIVE_SEND
        cmd.NSID = nsid
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        cmd.CDW[10] = (sizeof(dptr) >> 2) - 1
        cmd.CDW[11] = cdw11.DWORD
        cmd.CDW[12] = cdw12

        return self.admin_passthru(cmd, **kwargs)

    def directive_receive(self, dptr, doper=0, dtype=0, dspec=0, cdw12=0, nsid=1, **kwargs):
        cdw11 = DirectiveDW11()
        cdw11.DOPER = doper
        cdw11.DTYPE = dtype
        cdw11.DSPEC = dspec

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.DIRECTIVE_RECEIVE
        cmd.NSID = nsid
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        cmd.CDW[10] = (sizeof(dptr) >> 2) - 1
        cmd.CDW[11] = cdw11.DWORD
        cmd.CDW[12] = cdw12

        return self.admin_passthru(cmd, **kwargs)

    def nvme_mi_receive(self, dptr, nmsp0, **kwargs):
        cdw10 = NVMeMIDW10()
        cdw10.NMSP0 = nmsp0

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.NVME_MI_RECEIVE
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        cmd.CDW[10] = cdw10.DWORD

        return self.admin_passthru(cmd, **kwargs), cmd.RESULT

    def nvme_mi_send(self, dptr, nmsp0, **kwargs):
        cdw10 = NVMeMIDW10()
        cdw10.NMSP0 = nmsp0

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.NVME_MI_SEND
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        cmd.CDW[10] = cdw10.DWORD

        return self.admin_passthru(cmd, **kwargs)

    def fw_commit(self, ca=3, fs=1, bpid=0, **kwargs):
        cdw10 = FWCommitDW10()
        cdw10.BPID = bpid
        cdw10.CA = ca
        cdw10.FS = fs

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.FIRMWARE_COMMIT
        cmd.CDW[10] = cdw10.DWORD

        return self.admin_passthru(cmd, **kwargs)

    def fw_download(self, filename, xfer=0, offset=0, align=4096, **kwargs):
        file_size = os.path.getsize(filename)
        length = math.ceil(file_size / 4096) * 4096
        dptr = (c_uint8 * length)()
        memmove(dptr, open(filename, "rb").read(), file_size)
        addr = addressof(dptr)

        offset <<= 2
        if xfer == 0 or xfer % align:
            xfer = 4096

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.FIRMWARE_DOWNLOAD

        while file_size > 0:
            xfer = min(xfer, file_size)

            cmd.CDW[10] = (xfer >> 2) - 1
            cmd.CDW[11] = offset >> 2
            cmd.DATA_LEN = xfer
            cmd.DATA = addr

            status = self.admin_passthru(cmd, **kwargs)
            if status:
                return status

            addr += xfer
            file_size -= xfer
            offset += xfer

        return 0

    def get_features(self, fid, sel, cdw11=0, nsid=1, **kwargs):
        cdw10 = GetFeaturesDword10()
        cdw10.FID = fid
        cdw10.SEL = sel

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.GET_FEATURES
        cmd.NSID = nsid
        cmd.CDW[10] = cdw10.DWORD
        cmd.CDW[11] = cdw11

        if fid in GET_FEATURE_ENTRY:
            length = 4096 // sizeof(GET_FEATURE_ENTRY[fid])
            dptr = (GET_FEATURE_ENTRY[fid] * length)()
            cmd.DATA = addressof(dptr)
            cmd.DATA_LEN = 4096
        else:
            dptr = None

        status = self.admin_passthru(cmd, **kwargs)
        cdw0 = GET_FEATURE_ID.get(fid, CDW)()
        cdw0.DWORD = cmd.RESULT
        return status, cdw0, dptr

    def get_log(self, dptr, lid=0x1, lpol=0, lpou=0, lsp=0, xfer=4096, nsid=0xffffffff, **kwargs):
        addr = addressof(dptr)
        size = sizeof(dptr)

        cdw10 = GetLogPagDword10()
        cdw11 = GetLogPagDword11()

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.GET_LOG_PAGE
        cmd.NSID = nsid

        while size > 0:
            xfer = min(xfer, size)
            numd = (xfer >> 2) - 1

            cdw10.LID = lid
            cdw10.LSP = lsp
            cdw10.NUMDL = numd & 0xffff
            cdw11.NUMDU = numd >> 16

            cmd.CDW[10] = cdw10.DWORD
            cmd.CDW[11] = cdw11.DWORD
            cmd.CDW[12] = lpol
            cmd.CDW[13] = lpou
            cmd.DATA = addr
            cmd.DATA_LEN = xfer

            status = self.admin_passthru(cmd, **kwargs)
            if status:
                return status

            addr += xfer
            size -= xfer
            lpou, lpol = divmod(lpol + xfer, 2 ** 32)

        return 0

    def identify(self, nsid=0, cns=0, cntid=0, **kwargs):
        cdw10 = IdentifyDword10()
        cdw10.CNS = cns
        cdw10.CNTID = cntid

        dptr = IDENTIFY_CNS.get(cns, (c_uint8 * 4096))()

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.IDENTIFY
        cmd.NSID = nsid
        cmd.CDW[10] = cdw10.DWORD
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)

        return self.admin_passthru(cmd, **kwargs), dptr

    def namespace_attachment(self, sel, cntid_list, nsid=1, **kwargs):
        cdw10 = AttachNSDword10()
        cdw10.SEL = sel

        dptr = ControllerList()
        dptr.NUM = len(cntid_list)
        for i, cntid in enumerate(cntid_list):
            dptr.ID[i] = cntid

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.NAMESPACE_ATTACH
        cmd.NSID = nsid
        cmd.CDW[10] = cdw10.DWORD
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        return self.admin_passthru(cmd, **kwargs)

    def namespace_management(self, sel, nsze=0, ncap=0, flbas=0, dps=0, nmic=0, nsid=0, **kwargs):
        cdw10 = NamespaceManagementDword10()
        cdw10.SEL = sel

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.NAMESPACE_MGT
        cmd.CDW[10] = cdw10.DWORD

        if sel == 0:  # Create
            dptr = NamespaceManagementDataStructure()
            dptr.NSZE = nsze
            dptr.NCAP = ncap
            dptr.FLBAS = flbas
            dptr.DPS = dps
            dptr.NMIC = nmic

            cmd.NSID = 0
            cmd.DATA = addressof(dptr)
            cmd.DATA_LEN = sizeof(dptr)
        elif sel == 1:  # Delete
            cmd.NSID = nsid

        return self.admin_passthru(cmd, **kwargs), cmd.RESULT

    def set_features(self, fid, save=0, cdw11=0, cdw12=0, cdw13=0, cdw14=0, cdw15=0, dptr=None, nsid=0xffffffff,
                     **kwargs):
        cdw10 = SetFeaturesDword10()
        cdw10.FID = fid
        cdw10.SV = save

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.SET_FEATURES
        cmd.NSID = nsid
        cmd.CDW[10] = cdw10.DWORD
        cmd.CDW[11] = cdw11
        cmd.CDW[12] = cdw12
        cmd.CDW[13] = cdw13
        cmd.CDW[14] = cdw14
        cmd.CDW[15] = cdw15
        if dptr:
            cmd.DATA = addressof(dptr)
            cmd.DATA_LEN = sizeof(dptr)

        return self.admin_passthru(cmd, **kwargs)

    def sanitize(self, sanact=0, ause=0, owpass=0, oipbp=0, ndas=0, ovpra=0, nsid=0, **kwargs):
        cmd = NVMePassthruCmd()
        cdw10 = SanitizeDW10()
        cmd.OPCODE = OPCODE.SANITIZE
        cmd.NSID = nsid
        cdw10.SANACT = sanact
        cdw10.AUSE = ause
        cdw10.OWPASS = owpass
        cdw10.OIPBP = oipbp
        cdw10.NDAS = ndas

        cmd.CDW[10] = cdw10.DWORD
        cmd.CDW[11] = ovpra

        return self.admin_passthru(cmd, **kwargs)

    def virtualization_management(self, cntlid, rt, act, nr=0, **kwargs):
        cmd = NVMePassthruCmd()
        cdw10 = VirtualizationManagementDword10()
        cdw11 = VirtualizationManagementDword11()

        cmd.OPCODE = OPCODE.VIRT_MANAGEMENT
        cdw10.ACT = act
        cdw10.RT = rt
        cdw10.CNTLID = cntlid
        cdw11.NR = nr

        cmd.CDW[10] = cdw10.DWORD
        cmd.CDW[11] = cdw11.DWORD

        return self.admin_passthru(cmd, **kwargs)

    def format(self, nsid=1, lbaf=0, mset=0, pif=0, pil=0, ses=0, **kwargs):
        """
        Admin Command Set - Format NVM command
        :param lbaf:    LBA Format (LBAF)
        :param nsid:    NameSpace ID (NSID)
        :param mset:    Metadata Settings (MSET)
        :param pif:     Protection Information (PIF)
        :param pil:     Protection Information Location (PIL)
        :param ses:     Secure Erase Settings (SES)
        :return:        Status Field Of CQE
        """
        cdw10 = FormatDword10()
        cdw10.LBAF = lbaf
        cdw10.MSET = mset
        cdw10.PIF = pif
        cdw10.PIL = pil
        cdw10.SES = ses

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.FORMAT_NVM
        cmd.NSID = nsid
        cmd.CDW[10] = cdw10.DWORD

        return self.admin_passthru(cmd, **kwargs)

    def security_receive(self, nsid=1, nssf=0, spsp0=0, spsp1=0, secp=0, atl=0, **kwargs):
        cdw10 = SecurityReceiveDword10()
        cdw10.NSSF = nssf
        cdw10.SPSP0 = spsp0
        cdw10.SPSP1 = spsp1
        cdw10.SECP = secp

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.SECURITY_RECV
        cmd.NSID = nsid
        cmd.CDW[10] = cdw10.DWORD
        cmd.CDW[11] = atl

        return self.admin_passthru(cmd, **kwargs)

    def security_send(self, nsid=1, nssf=0, spsp0=0, spsp1=0, secp=0, atl=0, **kwargs):
        cdw10 = SecuritySendDword10()
        cdw10.NSSF = nssf
        cdw10.SPSP0 = spsp0
        cdw10.SPSP1 = spsp1
        cdw10.SECP = secp

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.SECURITY_SEND
        cmd.NSID = nsid
        cmd.CDW[10] = cdw10.DWORD
        cmd.CDW[11] = atl

        return self.admin_passthru(cmd, **kwargs)


class IO(IOCTL):
    def compare(self, slba, nlb, dptr, mptr=None, nsid=1, prinfo=0, fua=0, lr=0, reftag=0, apptag=0, appmask=0,
                **kwargs):
        cdw12 = RWDword12()
        cdw12.NLB = nlb - 1
        cdw12.PRINFO = prinfo
        cdw12.FUA = fua
        cdw12.LR = lr

        cmd = NVMeUserIO()
        cmd.OPCODE = OPCODE.COMPARE
        cmd.NSID = nsid
        cmd.SLBA = slba
        cmd.NBLOCKS = cdw12.NBLOCKS
        cmd.CONTROL = cdw12.CONTROL
        cmd.DATA = addressof(dptr)
        cmd.META = addressof(mptr) if mptr else 0
        cmd.REFTAG = reftag
        cmd.APPTAG = apptag
        cmd.APPMASK = appmask

        return self.nvme_io(cmd, **kwargs)

    def dataset_management(self, nr, dptr, idr=0, idw=0, ad=1, nsid=1, **kwargs):
        cdw10 = DsmDword10()
        cdw10.NR = nr - 1

        cdw11 = DsmDword11()
        cdw11.IDR = idr
        cdw11.IDW = idw
        cdw11.AD = ad

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.DATASET_MGT
        cmd.NSID = nsid
        cmd.CDW[10] = cdw10.DWORD
        cmd.CDW[11] = cdw11.DWORD
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)

        return self.io_passthru(cmd, **kwargs)

    def flush(self, nsid=1, **kwargs):
        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.FLUSH
        cmd.NSID = nsid

        return self.io_passthru(cmd, **kwargs)

    def read(self, slba, nlb, dptr, mptr=None, prinfo=0, fua=0, lr=0, dsm=0, reftag=0, apptag=0, appmask=0, **kwargs):
        cdw12 = RWDword12()
        cdw12.NLB = nlb - 1
        cdw12.PRINFO = prinfo
        cdw12.FUA = fua
        cdw12.LR = lr

        cmd = NVMeUserIO()
        cmd.OPCODE = OPCODE.READ
        cmd.SLBA = slba
        cmd.NBLOCKS = cdw12.NBLOCKS
        cmd.CONTROL = cdw12.CONTROL
        cmd.DATA = addressof(dptr)
        cmd.META = addressof(mptr) if mptr else 0
        cmd.DSMGMT = dsm
        cmd.REFTAG = reftag
        cmd.APPTAG = apptag
        cmd.APPMASK = appmask

        return self.nvme_io(cmd, **kwargs)

    def reservation_acquire(self, racqa, iekey, rtype, crkey, prkey, nsid=1, **kwargs):
        cdw10 = ReservationAcquire()
        cdw10.RACQA = racqa
        cdw10.IEKEY = iekey
        cdw10.RTYPE = rtype

        dptr = ReservationAcquireDataStructure()
        dptr.CRKEY = crkey
        dptr.PRKEY = prkey

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.RESERVATION_ACQUIRE
        cmd.NSID = nsid
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        cmd.CDW[10] = cdw10.DWORD

        return self.io_passthru(cmd, **kwargs)

    def reservation_register(self, rrega, iekey, cptpl, crkey, nrkey, nsid=1, **kwargs):
        cdw10 = ReservationRegister()
        cdw10.RREGA = rrega
        cdw10.IEKEY = iekey
        cdw10.CPTPL = cptpl

        dptr = ReservationRegisterDataStructure()
        dptr.CRKEY = crkey
        dptr.NRKEY = nrkey

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.RESERVATION_REGISTER
        cmd.NSID = nsid
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        cmd.CDW[10] = cdw10.DWORD

        return self.io_passthru(cmd, **kwargs)

    def reservation_release(self, rrela, iekey, rtype, crkey, nsid=1, **kwargs):
        cdw10 = ReservationRelease()
        cdw10.RRELA = rrela
        cdw10.IEKEY = iekey
        cdw10.RTYPE = rtype

        dptr = ReservationReleaseDataStructure()
        dptr.CRKEY = crkey

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.RESERVATION_RELEASE
        cmd.NSID = nsid
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        cmd.CDW[10] = cdw10.DWORD

        return self.io_passthru(cmd, **kwargs)

    def reservation_report(self, eds, nsid=1, **kwargs):
        if eds == 0:
            dptr = ReservationStatusDataStructure()
        else:
            dptr = ReservationStatusExtendedDataStructure()

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.RESERVATION_REPORT
        cmd.NSID = nsid
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        cmd.CDW[10] = (sizeof(dptr) >> 2) - 1
        cmd.CDW[11] = eds & 0x1

        return self.io_passthru(cmd, **kwargs), dptr

    def write(self, slba, nlb, dptr, mptr=None, dtype=0, prinfo=0, fua=0, lr=0, dsm=0, dspec=0, reftag=0, apptag=0,
              appmask=0, **kwargs):
        cdw12 = RWDword12()
        cdw12.NLB = nlb - 1
        cdw12.DTYPE = dtype
        cdw12.PRINFO = prinfo
        cdw12.FUA = fua
        cdw12.LR = lr

        cdw13 = RWDword13()
        cdw13.DSM = dsm
        cdw13.DSPEC = dspec

        cmd = NVMeUserIO()
        cmd.OPCODE = OPCODE.WRITE
        cmd.SLBA = slba
        cmd.NBLOCKS = cdw12.NBLOCKS
        cmd.CONTROL = cdw12.CONTROL
        cmd.DATA = addressof(dptr)
        cmd.META = addressof(mptr) if mptr else 0
        cmd.DSMGMT = cdw13.DWORD
        cmd.REFTAG = reftag
        cmd.APPTAG = apptag
        cmd.APPMASK = appmask

        return self.nvme_io(cmd, **kwargs)

    def write_uncorrectable(self, slba, nlb, nsid=1, **kwargs):
        cdw12 = RWDword12()
        cdw12.NLB = nlb - 1

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.WRITE_UNCORRECTABLE
        cmd.NSID = nsid
        cmd.CDW[10] = slba & 0xffffffff
        cmd.CDW[11] = slba >> 32
        cmd.CDW[12] = cdw12.DWORD

        return self.io_passthru(cmd, **kwargs)

    def write_zeroes(self, slba, nlb, nsid=1, deac=0, prinfo=0, fua=0, lr=0, reftag=0, apptag=0, appmask=0, **kwargs):
        cdw12 = RWDword12()
        cdw12.NLB = nlb - 1
        cdw12.DEAC = deac
        cdw12.PRINFO = prinfo
        cdw12.FUA = fua
        cdw12.LR = lr

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.WRITE_ZEROES
        cmd.NSID = nsid
        cmd.CDW[10] = slba & 0xffffffff
        cmd.CDW[11] = slba >> 32
        cmd.CDW[12] = cdw12.DWORD
        cmd.CDW[14] = reftag
        cmd.CDW[15] = apptag | (appmask << 16)

        return self.io_passthru(cmd, **kwargs)


class PIOCTL(IOCTL):
    NVME_IOCTL_ADMIN_CMD = _iowr('E', 0x01, NVMePassthruCmd)
    NVME_IOCTL_IO = _iowr('E', 0x02, PNVMeIOCmd)
    NVME_IOCTL_AIO = _iowr('E', 0x03, PNVMeIOCmd)
    NVME_IOCTL_ATOMIC = _iowr('E', 0x04, PNVMeIOCmd)
    NVME_IOCTL_PI = _iowr('E', 0x05, PNVMeIOCmd)
    NVME_IOCTL_SGL = _iowr('E', 0x06, PNVMeIOCmd)
    NVME_IOCTL_CRT_CQ = _iowr('E', 0x07, NVMePassthruCmd)
    NVME_IOCTL_DEL_CQ = _iowr('E', 0x08, NVMePassthruCmd)
    NVME_IOCTL_CRT_SQ = _iowr('E', 0x09, NVMePassthruCmd)
    NVME_IOCTL_DEL_SQ = _iowr('E', 0x0a, NVMePassthruCmd)

    NVME_IOCTL_SQ = _iowr('G', 0x01, c_uint32)
    NVME_IOCTL_CQ = _iowr('G', 0x02, c_uint32)
    NVME_IOCTL_DEBUG = _iowr('G', 0x03, c_uint32)

    def __init__(self, device='/dev/pnvme', cntid=0, nsid=1):
        super().__init__(cntid, nsid)
        self._c_fd = -1
        self._c_dev = device

    def __del__(self):
        self._close_c_fd()

    def close(self):
        self.__del__()

    def io_passthru(self, cmd, **kwargs):
        assert False, 'Not support io_passthru for PIOCTL'

    def reset(self, **kwargs):
        assert False, 'Not support reset for PIOCTL'

    def subsys_reset(self, **kwargs):
        assert False, 'Not support subsys_reset for PIOCTL'

    def nvme_debug(self, cmd):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_DEBUG, cmd)

    def nvme_get_sq(self, cmd):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_SQ, cmd)

    def nvme_get_cq(self, cmd):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_CQ, cmd)

    def nvme_io(self, cmd, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_IO, cmd, **kwargs)

    def nvme_pi(self, cmd, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_PI, cmd, **kwargs)

    def nvme_sgl(self, cmd, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_SGL, cmd, **kwargs)

    def nvme_aio(self, cmd, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_AIO, cmd, **kwargs)

    def nvme_atomic(self, cmd, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_ATOMIC, cmd, **kwargs)

    def admin_passthru(self, cmd, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_ADMIN_CMD, cmd, **kwargs)

    def nvme_crt_cq(self, cmd, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_CRT_CQ, cmd, **kwargs)

    def nvme_del_cq(self, cmd, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_DEL_CQ, cmd, **kwargs)

    def nvme_crt_sq(self, cmd, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_CRT_SQ, cmd, **kwargs)

    def nvme_del_sq(self, cmd, **kwargs):
        return self._ioctl(self.char_fd, self.NVME_IOCTL_DEL_SQ, cmd, **kwargs)

    def identify(self, nsid=1, cns=1, cntid=0, **kwargs):
        cdw10 = IdentifyDword10()
        cdw10.CNS = cns
        cdw10.CNTID = cntid
        dptr = ControllerDataStructure()
        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.IDENTIFY
        cmd.NSID = nsid
        cmd.CDW[10] = cdw10.DWORD
        cmd.ADDR = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        return self.admin_passthru(cmd, **kwargs), dptr

    def create_io_cq(self, qid, qsize, pc=1, ien=1, iv=0, **kwargs):
        cdw10 = CreateIOCQDword10()
        cdw10.QID = qid
        cdw10.QSIZE = qsize - 1

        cdw11 = CreateIOCQDword11()
        cdw11.PC = pc
        cdw11.IEN = ien
        cdw11.IV = iv

        dptr = (c_uint32 * (4 * qsize))()

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.CREATE_IO_CQ
        cmd.CDW[10] = cdw10.DWORD
        cmd.CDW[11] = cdw11.DWORD
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)

        return self.nvme_crt_cq(cmd, **kwargs)

    def create_io_sq(self, qid, qsize, pc=1, qprio=1, cqid=0, **kwargs):
        cdw10 = CreateIOCQDword10()
        cdw10.QID = qid
        cdw10.QSIZE = qsize - 1

        cdw11 = CreateIOSQDword11()
        cdw11.PC = pc
        cdw11.QPRIO = qprio
        cdw11.CQID = cqid

        dptr = (c_uint32 * (16 * qsize))()

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.CREATE_IO_SQ
        cmd.CDW[10] = cdw10.DWORD
        cmd.CDW[11] = cdw11.DWORD
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)

        return self.nvme_crt_sq(cmd, **kwargs)

    def delete_io_cq(self, qid, **kwargs):
        cdw10 = DeleteIOCQDword10()
        cdw10.QID = qid

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.DELETE_IO_CQ
        cmd.CDW[10] = cdw10.DWORD

        return self.nvme_del_cq(cmd, **kwargs)

    def delete_io_sq(self, qid, **kwargs):
        cdw10 = DeleteIOSQDword10()
        cdw10.QID = qid

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.DELETE_IO_SQ
        cmd.CDW[10] = cdw10.DWORD

        return self.nvme_del_sq(cmd, **kwargs)

    def write(self, slba, nlb, dptr, mptr=None, qid=1, nsid=1, dsm=0, **kwargs):
        cmd = PNVMeIOCmd()
        cmd.OPCODE = OPCODE.WRITE
        cmd.SLBA = slba
        cmd.NLB = nlb - 1
        cmd.QID = qid
        cmd.NSID = nsid
        cmd.PRP1 = addressof(dptr)
        cmd.META = addressof(mptr) if mptr else 0
        cmd.DSMGMT = dsm
        return self.nvme_io(cmd, **kwargs)

    def read(self, slba, nlb, dptr, mptr=None, qid=1, nsid=1, dsm=0, **kwargs):

        cmd = PNVMeIOCmd()
        cmd.OPCODE = OPCODE.READ
        cmd.SLBA = slba
        cmd.NLB = nlb - 1
        cmd.QID = qid
        cmd.NSID = nsid
        cmd.PRP1 = addressof(dptr)
        cmd.META = addressof(mptr) if mptr else 0
        cmd.DSMGMT = dsm
        return self.nvme_io(cmd, **kwargs)

    def write_sgl(self, slba, nlb, d_num, m_num, dptr, dsglptr, mptr=None, msglptr=None, qid=1, nsid=1, ctrl=0,
                  flags=0x40, doff=0, moff=0, **kwargs):
        cmd = NVMeSGLIO()
        cmd.OPCODE = OPCODE.WRITE
        cmd.SLBA = slba
        cmd.NLB = nlb - 1
        cmd.QID = qid
        cmd.NSID = nsid
        cmd.PRP1 = addressof(dptr)
        cmd.META = addressof(mptr) if mptr else 0
        cmd.CTRL = ctrl
        cmd.FLAGS = flags
        cmd.DATA_OFF = doff
        cmd.META_OFF = moff
        cmd.DATA_DES_NUM = d_num if d_num >= 1 else 1
        cmd.META_DES_NUM = m_num
        cmd.SGL_DATA_PTR = addressof(dsglptr)
        cmd.SGL_META_PTR = addressof(msglptr) if mptr else 0
        return self.nvme_sgl(cmd, **kwargs)

    def read_sgl(self, slba, nlb, d_num, m_num, dptr, dsglptr, mptr=None, msglptr=None, qid=1, nsid=1, ctrl=0,
                 flags=0x40, doff=0, moff=0, **kwargs):
        cmd = NVMeSGLIO()
        cmd.OPCODE = OPCODE.READ
        cmd.SLBA = slba
        cmd.NLB = nlb - 1
        cmd.QID = qid
        cmd.NSID = nsid
        cmd.PRP1 = addressof(dptr)
        cmd.META = addressof(mptr) if mptr else 0
        cmd.CTRL = ctrl
        cmd.FLAGS = flags
        cmd.DATA_OFF = doff
        cmd.META_OFF = moff
        cmd.DATA_DES_NUM = d_num if d_num >= 1 else 1
        cmd.META_DES_NUM = m_num
        cmd.SGL_DATA_PTR = addressof(dsglptr)
        cmd.SGL_META_PTR = addressof(msglptr) if mptr else 0
        return self.nvme_sgl(cmd, **kwargs)

    def write_async(self, slba, nlb, qid=1, nsid=1, **kwargs):
        cmd = PNVMeIOCmd()
        cmd.OPCODE = OPCODE.WRITE
        cmd.SLBA = slba
        cmd.NLB = nlb - 1
        cmd.QID = qid
        cmd.NSID = nsid
        return self.nvme_aio(cmd, **kwargs)

    def read_async(self, slba, nlb, qid=1, nsid=1, **kwargs):
        cmd = PNVMeIOCmd()
        cmd.OPCODE = OPCODE.READ
        cmd.SLBA = slba
        cmd.NLB = nlb - 1
        cmd.QID = qid
        cmd.NSID = nsid
        return self.nvme_aio(cmd, **kwargs)

    def write_atomic(self, slba, nlb, qid=1, nsid=1, pat=0, **kwargs):
        cmd = PNVMeIOCmd()
        cmd.OPCODE = OPCODE.WRITE
        cmd.SLBA = slba
        cmd.NLB = nlb - 1
        cmd.QID = qid
        cmd.NSID = nsid
        cmd.CTRL = pat
        return self.nvme_atomic(cmd, **kwargs)

    def read_atomic(self, slba, nlb, qid=1, nsid=1, **kwargs):
        cmd = PNVMeIOCmd()
        cmd.OPCODE = OPCODE.READ
        cmd.SLBA = slba
        cmd.NLB = nlb - 1
        cmd.QID = qid
        cmd.NSID = nsid
        return self.nvme_atomic(cmd, **kwargs)

    def async_trace(self):
        dptr = AsyncTrace()
        cmd = PNVMeDebug()
        cmd.OPCODE = DebugOPCODE.ASYNC_TRACE
        cmd.DATA = addressof(dptr)
        ret = self.nvme_debug(cmd)
        return ret, dptr

    def get_cq(self, qid=0):
        return self.nvme_get_cq(qid)

    def get_sq(self, qid=0):
        return self.nvme_get_sq(qid)

    def write_pi(self, slba, nlb, dptr, mptr=None, qid=1, nsid=1, ctrl=0, reftag=0, apptag=0, appmask=0, **kwargs):
        cmd = PNVMeIOCmd()
        cmd.OPCODE = OPCODE.WRITE
        cmd.SLBA = slba
        cmd.NLB = nlb - 1
        cmd.QID = qid
        cmd.NSID = nsid
        cmd.CTRL = ctrl
        cmd.PRP1 = addressof(dptr)
        cmd.META = addressof(mptr) if mptr else 0
        cmd.REFTAG = reftag
        cmd.APPTAG = apptag
        cmd.APPMASK = appmask
        return self.nvme_pi(cmd, **kwargs)

    def read_pi(self, slba, nlb, dptr, mptr=None, qid=1, nsid=1, ctrl=0, reftag=0, apptag=0, appmask=0, **kwargs):

        cmd = PNVMeIOCmd()
        cmd.OPCODE = OPCODE.READ
        cmd.SLBA = slba
        cmd.NLB = nlb - 1
        cmd.QID = qid
        cmd.NSID = nsid
        cmd.CTRL = ctrl
        cmd.PRP1 = addressof(dptr)
        cmd.META = addressof(mptr) if mptr else 0
        cmd.REFTAG = reftag
        cmd.APPTAG = apptag
        cmd.APPMASK = appmask
        return self.nvme_pi(cmd, **kwargs)
