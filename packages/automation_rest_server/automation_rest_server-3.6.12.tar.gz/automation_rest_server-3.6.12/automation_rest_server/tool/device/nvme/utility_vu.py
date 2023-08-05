#!/usr/bin/env python
# pylint: disable=too-many-locals,too-many-arguments,superfluous-parens,import-error,invalid-name,arguments-differ
"""
Created on 2019/4/26

@author: yyang
"""
from ctypes import *
from tool.device.nvme.struct import *
from utils import log
from tool.device.nvme.buf import *


class VUProjectType:

    def __init__(self):
        pass

    @classmethod
    def from_name(cls, name):
        """
            Return the class which matches ``name`` if it exists inside this
            module or raise an exception.
        """
        if name not in globals():
            raise NotImplementedError('Project of type %s is not supported' % name)
        return globals()[name]


class TahoeVU(VUProjectType):
    def __init__(self, dev):
        super().__init__()
        self.dev = dev
        log.INFO("Tahoe VU class init!")

    def malloc(self, size):
        ptr = self.dev.dll.nvme_alloc(size)
        assert ptr != 0, 'Malloc {:#x} Failed!'.format(size)
        return ptr

    def show_test_case(self, show_string):
        """Show test case in UART log
        Domain      DW10       DW11       DW12   DW13    DW14  DW15   DW0(CQE)
        | Media  |  0x10001007  |  1024 |  None |  None  | None | None| None

        This is VU command for showing test case in UART log
        Args:
           None
        Returns:
           None
        Raises:
           send VU cmd fail
        """
        str1 = show_string.encode()
        size = 512  # size must be 512, otherwise standard driver can not allocate memory
        dptr = create_string_buffer(str1, size)
        ptr = self.malloc(size)
        try:
            self.dev.dll.nvme_copy(c_void_p(ptr), dptr, size)

            cmd = NVMePassthruCmd()
            cmd.OPCODE = 0xC0
            cmd.CDW[10] = 0x10001007
            cmd.CDW[11] = 1024
            cmd.DATA = ptr
            cmd.DATA_LEN = size
            #log.INFO("%x", ptr)
            #log.INFO(list(dptr))
            return self.dev.admin_passthru(cmd)
        finally:
            self.dev.dll.nvme_free(c_void_p(ptr))

    def get_power_consumption(self, length=64):
        """get_async_event_info

            Domain         DW10       DW11         DW12               DW13    DW14   DW15  DW0(CQE)
        |Host/Platform| 0x10002028  | 4    |        None            | None  | None  | None| None

        Args:
            None
        Returns:
            power consumption data: Word0: Voltage, Word1: Current
        """
        dptr = TahoeVUPower()
        cmd = NVMePassthruCmd()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x10002028
        cmd.CDW[11] = length
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        self.dev.admin_passthru(cmd)
        vol = dptr.vol
        cur = dptr.cur
        ret = float(str(vol)+'.'+str(cur))
        #log.INFO("Get Power Consumption syccessfully[int: %x, float: %x].", vol, cur)
        log.INFO("Get Power Consumption syccessfully[Power: %f].", ret)
        log.INFO("Get Power Consumption syccessfully[Credit: max:%d, min:%d, avg:%d].",\
                 dptr.max_credit, dptr.min_credit, dptr.avg_credit)
        return ret, dptr.max_credit, dptr.min_credit, dptr.avg_credit

    def get_memory(self, addr, length=1, cpu=0):
        dptr = (c_uint32 * length)()
        cmd = NVMePassthruCmd()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x10002005
        cmd.CDW[11] = length
        cmd.CDW[12] = cpu
        cmd.CDW[13] = addr
        cmd.CDW[14] = length * 4
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        self.dev.admin_passthru(cmd)
        return dptr

    def set_memory(self, addr, dptr, length=0, cpu=0):
        ptr = self.malloc(sizeof(dptr))

        try:
            length = length if length else sizeof(dptr) // 4
            self.dev.dll.nvme_copy(c_void_p(ptr), dptr, length * 4)

            cmd = NVMePassthruCmd()
            cmd.OPCODE = 0xC0
            cmd.CDW[10] = 0x10001006
            cmd.CDW[11] = length
            cmd.CDW[12] = cpu
            cmd.CDW[13] = addr
            cmd.CDW[14] = length * 4
            cmd.DATA = ptr
            cmd.DATA_LEN = sizeof(dptr)
            return self.dev.admin_passthru(cmd)
        finally:
            self.dev.dll.nvme_free(c_void_p(ptr))

    def get_idle_state(self):

        #dptr = (c_uint16 * (length//2))()
        cmd = NVMePassthruCmd()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x10002042
        cmd.CDW[11] = 1
        #cmd.DATA = addressof(dptr)
        #cmd.DATA_LEN = sizeof(dptr)
        self.dev.admin_passthru(cmd)
        return cmd.RESULT


    def force_gc(self, blk):

        cmd = NVMePassthruCmd()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x2000000C
        cmd.CDW[12] = blk

        return self.dev.admin_passthru(cmd)

    def get_bmi_entry(self, blk):
        dptr = TahoeBMIEntry()
        cmd = NVMePassthruCmd()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x20002001
        cmd.CDW[11] = 32
        cmd.CDW[12] = 1
        cmd.CDW[13] = blk

        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        self.dev.admin_passthru(cmd)
        return dptr

    def force_flush(self, task="host", ftype="block"):
        cmd = NVMePassthruCmd()
        assert task in ["host", "gc", "ftl"], "task type not support!"
        assert ftype in ["raidline", "block", "pu", "pad", "wordline"], \
                "task type not support!"
        if task == "host":
            cmd.CDW[12] = 0
        elif task == "gc":
            cmd.CDW[12] = 1
        elif task == "ftl":
            cmd.CDW[12] = 2

        if ftype == "raidline":
            cmd.CDW[13] = 0
        elif ftype == "block":
            cmd.CDW[13] = 1
        elif ftype == "pu":
            cmd.CDW[13] = 2
        elif ftype == "pad":
            cmd.CDW[13] = 3
        elif ftype == "wordline":
            cmd.CDW[13] = 4
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x20000011

        return self.dev.admin_passthru(cmd)

    def get_int_type(self):
        """Get INT type
        Domain      DW10          DW11    DW12    DW13    DW14  DW15   DW0(CQE)
        | Media  |  0x10002034   |  4   |  None |  None  | None | None |  None
        Args:
            None
        Returns:
            INT type:INT0/INT1 or INT2
        Raises:
            send VU cmd fail
        """
        dptr = (c_uint8 * (32))()
        cmd = NVMePassthruCmd()
        dw10 = 0x10002034
        cmd.CDW[10] = dw10
        cmd.CDW[11] = 4
        cmd.OPCODE = 0xC0
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        self.dev.admin_passthru(cmd)
        tmp = map(chr, dptr[0:17])
        int_type = "".join(tmp)
        int_type = int_type.strip('\x00')
        log.INFO("INT type is %s", int_type)
        return int_type

    def get_cmd_cnt_per_queue(self, qid=1):
        """get_cmd_cnt_per_queue

            Domain         DW10       DW11    DW12   DW13    DW14   DW15  DW0(CQE)
        |Host/Platform| 0x10000043    | 0x0 |  qid |     None | None | None| None

        This is VU command for get command counter per queu
        Args:
            None
        Returns:
            cqe dw0: command counter per Queue
        """
        cmd = NVMePassthruCmd()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x10000043
        cmd.CDW[12] = qid
        #cmd.DATA = addressof(dptr)
        #cmd.DATA_LEN = sizeof(dptr)
        self.dev.admin_passthru(cmd)
        log.INFO("get_cmd_cnt_per_queue[q:%d, number:%d] successfully.", qid, cmd.RESULT)
        return cmd.RESULT

    def set_crecit(self, val):
        cmd = NVMePassthruCmd()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x10000046
        cmd.CDW[11] = 0
        cmd.CDW[12] = int(val)

        return self.dev.admin_passthru(cmd)

    def get_drive_security_state(self):
        """this function is getting drive security state  (ISE/SED/TCG not enable)

                Domain         DW10        DW11       DW12    DW13    DW14  DW15   DW0(CQE)
               | Generic   |  0x1000204f  |  0x04  |  0    |   0    |   0| None

               This is VU command for getting drive security state
               Args:
                   None
               Returns:
                   Returns TCG State:
                    byte 0 - 1: return data length (big-endian)
                    byte 2: 0 = SED, 1 = ISE
                    byte 3: 1 = TCG is finalized
               Raises:
                   send VU cmd fail
               """
        cmd = NVMePassthruCmd()
        dw10 = 0x1000204f
        dptr = (c_uint8 * 4096)()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = dw10
        cmd.CDW[11] = 0x04
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        self.dev.admin_passthru(cmd)
        return dptr
