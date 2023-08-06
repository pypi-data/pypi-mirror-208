#!/usr/bin/env python
# pylint: disable=too-many-locals,too-many-arguments,superfluous-parens,import-error,invalid-name,arguments-differ,
"""
Created on 2019/4/26

@author: yyang
"""
import math
from time import sleep
from tool.device.nvme.ioctl import IO, ADMIN
from tool.device.nvme.utility_vu import *


class NVMe(IO, ADMIN):
    def get_flbas(self, nsid=1, cntid=0):
        id_ns = self.identify_ns(nsid=nsid, cntid=cntid)
        return id_ns.FLBAS & 0xf

    def format_as(self, lbads=4096, ms=0, nsid=1, cntid=0, **kwargs):
        id_ns = self.identify_ns(nsid=nsid, cntid=cntid)
        for i, lbaf in enumerate(id_ns.LBAF):
            if lbads == 2 ** lbaf.LBADS and ms == lbaf.MS:
                self.format(nsid, i, **kwargs)
                return

        raise AssertionError('Invalid lbaf! lbads: {}, ms: {}'.format(lbads, ms))

    def attach_ns(self, cntid, nsid=1, **kwargs):
        ret = self.namespace_attachment(0, cntid, nsid=nsid, **kwargs)
        sleep(1)
        # some OS need reset to find block device
        # self.reset()
        # sleep(1)
        return ret

    def detach_ns(self, cntid, nsid=1, **kwargs):
        return self.namespace_attachment(1, cntid, nsid=nsid, **kwargs)

    def create_ns(self, nsze=0, ncap=0, flbas=0, dps=0, nmic=0, **kwargs):
        return self.namespace_management(0, nsze=nsze, ncap=ncap, flbas=flbas, dps=dps, nmic=nmic, **kwargs)

    def delete_ns(self, nsid, **kwargs):
        return self.namespace_management(1, nsid=nsid, **kwargs)

    def get_log_error_info(self, cntid=0):
        id_ctrl = self.identify_ctrl(cntid=cntid)
        dptr = (ErrorInformation * (id_ctrl.ELPE + 1))()
        self.get_log(dptr, lid=0x1)
        return dptr

    def get_log_smart_health_info(self):
        dptr = SmartHealthInformation()
        self.get_log(dptr, lid=0x2)
        return dptr

    def get_log_fw_slot_info(self):
        dptr = FirmwareSlotInformation()
        self.get_log(dptr, lid=0x3)
        return dptr

    def get_log_change_ns_list(self):
        dptr = DeviceSelfTest()
        self.get_log(dptr, lid=0x4)
        return dptr

    def get_log_cmd_supported_effects(self):
        dptr = CommandsSupportAndEffects()
        self.get_log(dptr, lid=0x5)
        return dptr

    def self_test(self, stc, testaction=0):
        pass

    def get_log_device_self_test(self):
        dptr = SelfTestLog()
        self.get_log(dptr, lid=0x6)
        return dptr

    def get_log_telemetry_host_init_log(self, lsp=0x0):
        dptr = TelemetryHostInitiated()
        self.get_log(dptr, lid=0x7, lsp=lsp)
        return dptr

    def get_log_telemetry_ctrl_init_log(self):
        dptr = TelemetryControllerInitiated()
        self.get_log(dptr, lid=0x8)
        return dptr

    def get_log_reservation_notification(self):
        dptr = ReservationNotificationLog()
        self.get_log(dptr, lid=0x80)
        return dptr

    def get_log_sanitize_status(self):
        dptr = SanitizeStatusLog()
        self.get_log(dptr, lid=0x81)
        return dptr

    def identify_ns(self, nsid=1, cntid=0):
        return self.identify(nsid=nsid, cns=0x0, cntid=cntid)[1]

    def identify_ctrl(self, cntid=0):
        return self.identify(nsid=0, cns=0x1, cntid=cntid)[1]

    def identify_active_ns_list(self, nsid=1, cntid=0):
        return self.identify(nsid=nsid, cns=0x2, cntid=cntid)[1]

    def identify_allocated_ns_list(self, nsid=1, cntid=0):
        return self.identify(nsid=nsid, cns=0x10, cntid=cntid)[1]

    def identify_attached_ctrl_list(self, nsid=1, cntid=0):
        return self.identify(nsid=nsid, cns=0x12, cntid=cntid)[1]

    def identify_existed_ctrl_list(self, cntid=0):
        return self.identify(nsid=0, cns=0x13, cntid=cntid)[1]

    def identify_primary_ctrl_cap(self, cntid=0):
        return self.identify(nsid=0, cns=0x14, cntid=cntid)[1]

    def identify_secondary_ctrl_list(self, cntid=0):
        return self.identify(nsid=0, cns=0x15, cntid=cntid)[1]

    def get_features_arbitration(self, sel=0):
        return self.get_features(FeatureID.Arbitration, sel)[1]

    def set_features_arbitration(self, save=0, ab=0, lpw=0, mpw=0, hpw=0, **kwargs):
        cdw11 = Arbitration()
        cdw11.AB = ab
        cdw11.LPW = lpw
        cdw11.MPW = mpw
        cdw11.HPW = hpw
        return self.set_features(0x1, save, cdw11.DWORD, **kwargs)

    def get_features_power_management(self, sel=0, **kwargs):
        return self.get_features(FeatureID.PowerManagement, sel, **kwargs)[1]

    def set_features_power_management(self, save=0, ps=0, wh=0, **kwargs):
        cdw11 = PowerManagement()
        cdw11.PS = ps
        cdw11.WH = wh
        return self.set_features(0x2, save, cdw11.DWORD, **kwargs)

    def get_features_lba_range_type(self, sel=0, nsid=1, **kwargs):
        return self.get_features(FeatureID.LBARangeType, sel, nsid=nsid, **kwargs)[1]

    def set_features_lba_range_type(self, lrt, save=0, nsid=1, **kwargs):
        cdw11 = LBARangeType()
        cdw11.NUM = len(lrt) - 1

        dptr = (LBARangeTypeEntry * 64)()
        for i, _lrt in enumerate(lrt):
            if isinstance(_lrt, dict):
                for key, val in _lrt.items():
                    if key == 'GUID':
                        setattr(dptr[i].GUID, 'LOW', val & 0xffffffffffffffff)
                        setattr(dptr[i].GUID, 'HIGH', val >> 64)
                    else:
                        setattr(dptr[i], key, val)
            else:
                for key, _ in getattr(_lrt, '_fields_'):
                    setattr(dptr[i], key, getattr(_lrt, key))
        return self.set_features(FeatureID.LBARangeType, save, cdw11.DWORD, dptr=dptr, nsid=nsid, **kwargs)

    def get_features_temperature_threshold(self, sel=0, **kwargs):
        return self.get_features(FeatureID.TemperatureThreshold, sel, **kwargs)[1]

    def set_features_temperature_threshold(self, save=0, tmpth=0, tmpsel=0, thsel=0, **kwargs):
        cdw11 = TemperatureThreshold()
        cdw11.TMPTH = tmpth
        cdw11.TMPSEL = tmpsel
        cdw11.THSEL = thsel
        return self.set_features(FeatureID.TemperatureThreshold, save, cdw11.DWORD, **kwargs)

    def get_features_host_memory_buffer(self, sel=0, **kwargs):
        return self.get_features(FeatureID.HostMemoryBuffer, sel, **kwargs)[2]

    def set_features_host_memory_buffer(self, save=0, ehm=0, mr=0, esize=0, hdmlec=0, **kwargs):
        cdw11 = HostMemoryBuffer()
        cdw11.EHM = ehm
        cdw11.MR = mr
        # get CC.MPS and init HMB size
        ccmps = 4096
        hsize = 0
        # config Descriptor List
        dptr = HostMemoryBufferDescriptorList()
        for i in range(hdmlec):
            # set entry
            dptr.ENTRY[i].BSIZE = esize
            dptr.ENTRY[i].BADD = addressof
            # cal HMB size
            hsize += (esize * ccmps)
        # get dwords info
        hmdlla = addressof(dptr) & 0xffffffff
        hmdlua = (addressof(dptr) >> 32) & 0xffffffff

        return self.set_features(FeatureID.HostMemoryBuffer, save, cdw11.DWORD, cdw12=hsize, cdw13=hmdlla,
                                 cdw14=hmdlua, cdw15=hdmlec, **kwargs)

    def get_features_non_operational_power_state_config(self, sel=0, **kwargs):
        return self.get_features(FeatureID.NonOperationalPowerStateConfig, sel, **kwargs)[2]

    def set_features_non_operational_power_state_config(self, nopsc, save=0, **kwargs):
        dptr = NonOperationalPowerStateConfig()
        dptr.NonOperationalPowerStateConfig = nopsc
        return self.set_features(FeatureID.NonOperationalPowerStateConfig, save, 0, dptr=dptr, **kwargs)

    def get_features_error_recovery(self, sel=0, nsid=1, **kwargs):
        return self.get_features(FeatureID.ErrorRecovery, sel, nsid=nsid, **kwargs)[1]

    def set_features_error_recovery(self, save=0, tler=0, dulbe=0, nsid=1, **kwargs):
        cdw11 = ErrorRecovery()
        cdw11.TLER = tler
        cdw11.DULBE = dulbe
        return self.set_features(FeatureID.ErrorRecovery, save, cdw11.DWORD, nsid=nsid, **kwargs)

    def get_features_volatile_write_cache(self, sel=0, **kwargs):
        return self.get_features(FeatureID.VolatileWriteCache, sel, **kwargs)[1]

    def set_features_volatile_write_cache(self, save=0, wce=0, **kwargs):
        cdw11 = VolatileWriteCache()
        cdw11.WCE = wce
        return self.set_features(FeatureID.VolatileWriteCache, save, cdw11.DWORD, **kwargs)

    def get_features_number_of_queues(self, sel=0, **kwargs):
        return self.get_features(FeatureID.NumberOfQueues, sel, **kwargs)[1]

    def set_features_number_of_queues(self, lrt, save=0, **kwargs):
        cdw11 = NumberOfQueues()
        cdw11.NSQR = len(lrt) - 1
        cdw11.NCQR = len(lrt) - 1

        dptr = (LBARangeTypeEntry * 64)()
        for i, _lrt in enumerate(lrt):
            if isinstance(_lrt, dict):
                for key, val in _lrt.items():
                    setattr(dptr[i], key, val)
            else:
                for key, _ in getattr(_lrt, '_fields_'):
                    setattr(dptr[i], key, getattr(_lrt, key))

        return self.set_features(FeatureID.NumberOfQueues, save, cdw11.DWORD, **kwargs)

    def get_features_interrupt_coalescing(self, sel=0, **kwargs):
        return self.get_features(FeatureID.InterruptCoalescing, sel, **kwargs)[1]

    def set_features_interrupt_coalescing(self, save=0, thr=0, time=0, **kwargs):
        cdw11 = InterruptCoalescing()
        cdw11.THR = thr
        cdw11.TIME = time
        return self.set_features(FeatureID.InterruptCoalescing, save, cdw11.DWORD, **kwargs)

    def get_features_interrupt_vector_configuration(self, sel=0, iv=1, **kwargs):
        cdw11 = InterruptVectorConfiguration()
        cdw11.IV = iv
        return self.get_features(FeatureID.InterruptVectorConfiguration, sel, cdw11=cdw11.DWORD, **kwargs)[1]

    def set_features_interrupt_vector_configuration(self, save=0, iv=0, cd=0, **kwargs):
        cdw11 = InterruptVectorConfiguration()
        cdw11.IV = iv
        cdw11.CD = cd
        return self.set_features(FeatureID.InterruptVectorConfiguration, save, cdw11.DWORD, **kwargs)

    def get_features_write_atomicity_normal(self, sel=0, **kwargs):
        return self.get_features(FeatureID.WriteAtomicityNormal, sel, **kwargs)[1]

    def set_features_write_atomicity_normal(self, save=0, dn=0, **kwargs):
        cdw11 = WriteAtomicityNormal()
        cdw11.DN = dn
        return self.set_features(FeatureID.WriteAtomicityNormal, save, cdw11.DWORD, **kwargs)

    def get_features_asynchronous_event_configuration(self, sel=0, **kwargs):
        return self.get_features(FeatureID.AsynchronousEventConfiguration, sel, **kwargs)[1]

    def set_features_asynchronous_event_configuration(self, save=0, shcw=0, nan=0, fan=0, tln=0, **kwargs):
        cdw11 = AsynchronousEventConfiguration()
        cdw11.SHCW = shcw
        cdw11.NAN = nan
        cdw11.FAN = fan
        cdw11.TLN = tln
        return self.set_features(FeatureID.AsynchronousEventConfiguration, save, cdw11.DWORD, **kwargs)

    def get_features_autonomous_power_state_transition(self, sel=0, **kwargs):
        return self.get_features(FeatureID.AutonomousPowerStateTransition, sel, **kwargs)[1]

    def set_features_autonomous_power_state_transition(self, save=0, apste=0, **kwargs):
        cdw11 = AutonomousPowerStateTransition()
        cdw11.APSTE = apste
        return self.set_features(FeatureID.AutonomousPowerStateTransition, save, cdw11.DWORD, **kwargs)

    def get_features_software_progress_marker(self, sel=0, **kwargs):
        return self.get_features(FeatureID.SoftwareProgressMarker, sel, **kwargs)[2]

    def set_features_software_progress_marker(self, save=0, pbslc=0, **kwargs):
        cdw11 = SoftwareProgressMarker()
        cdw11.PBSLC = pbslc
        return self.set_features(FeatureID.SoftwareProgressMarker, save, cdw11.DWORD, **kwargs)

    def get_features_host_identifier(self, sel=0, **kwargs):
        return self.get_features(FeatureID.HostIdentifier, sel, **kwargs)[2]

    def set_features_host_identifier(self, exhid, hostidl, hostidh, save=0, **kwargs):
        cdw11 = HostIdentifier()
        cdw11.EXHID = exhid
        dptr = HostIdentifierEntry()
        dptr.HOSTIDL = hostidl
        dptr.HOSTIDH = hostidh
        return self.set_features(FeatureID.HostIdentifier, save, cdw11.DWORD, dptr=dptr, **kwargs)

    def get_features_reservation_notification_mask(self, sel=0, **kwargs):
        return self.get_features(FeatureID.ReservationNotificationMask, sel, nsid=1, **kwargs)[2]

    def set_features_reservation_notification_mask(self, save=0, regpre=0, resrel=0, respre=0, **kwargs):
        cdw11 = ReservationNotificationMask()
        cdw11.REGPRE = regpre
        cdw11.RESREL = resrel
        cdw11.RESPRE = respre
        return self.set_features(FeatureID.ReservationNotificationMask, save, **kwargs)

    def get_features_reservation_persistence(self, sel=0, **kwargs):
        return self.get_features(FeatureID.ReservationPersistence, sel, nsid=1, **kwargs)[2]

    def set_features_reservation_persistence(self, save=0, ptpl=0, **kwargs):
        cdw11 = ReservationPersistence()
        cdw11.PTPL = ptpl
        return self.set_features(FeatureID.ReservationPersistence, save, nsid=1, **kwargs)

    def get_features_host_controlled_thermal_management(self, sel=0, **kwargs):
        return self.get_features(FeatureID.HostControlledThermalManagement, sel, **kwargs)[2]

    def set_features_host_controlled_thermal_management(self, save=0, tmt2=0, tmt1=0, **kwargs):
        cdw11 = HostControlledThermalManagement()
        cdw11.TMT2 = tmt2
        cdw11.TMT1 = tmt1
        return self.set_features(FeatureID.HostControlledThermalManagement, save, **kwargs)

    def get_features_timestamp(self, sel=0, **kwargs):
        return self.get_features(FeatureID.Timestamp, sel, **kwargs)[2]

    def set_features_timestamp(self, timestamp, save=0, **kwargs):
        dptr = Timestamp()
        dptr.TIMESTAMP = timestamp
        return self.set_features(FeatureID.Timestamp, save, 0, dptr=dptr, **kwargs)

    def get_features_sanitize_config(self, sel=0, **kwargs):
        return self.get_features(FeatureID.SanitizeConfig, sel, **kwargs)[2]

    def set_features_sanitize_config(self, save=0, nodrm=0, **kwargs):
        cdw11 = SanitizeConfig()
        cdw11.NODRM = nodrm
        return self.set_features(FeatureID.SanitizeConfig, save, **kwargs)

    def get_features_nonoperational_power_state_config(self, sel=0, **kwargs):
        return self.get_features(FeatureID.NonOperationalPowerStateConfig, sel, **kwargs)[2]

    def set_features_nonoperational_power_state_config(self, save=0, noppme=0, **kwargs):
        cdw11 = NonOperationalPowerStateConfig()
        cdw11.NOPPME = noppme
        return self.set_features(FeatureID.NonOperationalPowerStateConfig, save, **kwargs)


class CNEX(NVMe):
    def fw_inject_uecc_start(self):
        cmd = NVMePassthruCmd()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x1
        cmd.CDW[15] = 0x14
        return self.admin_passthru(cmd)

    def fw_inject_uecc_stop(self):
        cmd = NVMePassthruCmd()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x0
        cmd.CDW[15] = 0x14
        return self.admin_passthru(cmd)

    def read_register(self, addr):
        dptr = (c_uint32 * 1024)()
        cmd = NVMePassthruCmd()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x2
        cmd.CDW[11] = addr
        cmd.CDW[15] = 0x14
        cmd.DATA = addressof(dptr)
        cmd.DATA_LEN = sizeof(dptr)
        self.admin_passthru(cmd)
        return dptr[0]

    def write_register(self, addr, value):
        cmd = NVMePassthruCmd()
        cmd.OPCODE = 0xC0
        cmd.CDW[10] = 0x3
        cmd.CDW[11] = addr
        cmd.CDW[12] = value
        cmd.CDW[15] = 0x14
        return self.admin_passthru(cmd)

    def rdma_read_list(self, offset, ndw=1, nsid=1):
        length = math.ceil(ndw / 1024) * 1024
        data = (c_uint32 * length)()

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.CNEX_READ_MEM
        cmd.NSID = nsid
        cmd.CDW[10] = offset & 0xffffffff
        cmd.CDW[11] = offset >> 32
        cmd.CDW[12] = ndw - 1
        cmd.DATA = addressof(data)
        cmd.DATA_LEN = length * 4

        return self.io_passthru(cmd), data[0:ndw]

    def rdma_write_list(self, offset, array, nsid=1):
        ndw = len(array)
        length = math.ceil(ndw / 1024) * 1024
        data = (c_uint32 * length)(*array)

        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.CNEX_WRITE_MEM
        cmd.NSID = nsid
        cmd.CDW[10] = offset & 0xffffffff
        cmd.CDW[11] = offset >> 32
        cmd.CDW[12] = ndw - 1
        cmd.DATA = addressof(data)
        cmd.DATA_LEN = length * 4

        return self.io_passthru(cmd)

    def rdma_read(self, offset, nsid=1):
        _, value = self.rdma_read_list(offset, ndw=1, nsid=nsid)
        return value[0]

    def rdma_write(self, offset, value, nsid=1):
        return self.rdma_write_list(offset, [value], nsid=nsid)

    def get_bad_block(self, dptr, lpol=0, lpou=0):
        return self.get_log(dptr, lid=0xcb, lpol=lpol, lpou=lpou)

    def clear_gbb(self, gbb, nsid=0xffffffff):
        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.CNEX_CLEAR_GBB
        cmd.NSID = nsid
        cmd.CDW[10] = gbb
        cmd.CDW[12] = 0x84

        return self.admin_passthru(cmd)

    def aging_era_nand(self):
        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.AGING_MF
        cmd.CDW[12] = 0x4
        return self.admin_passthru(cmd)

    def aging_scan_fbb(self):
        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.AGING_MF
        cmd.CDW[12] = 0x3
        return self.admin_passthru(cmd)

    def aging_era_dirty(self):
        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.AGING_MF
        cmd.CDW[12] = 0xb
        return self.admin_passthru(cmd)

    def read_retry_ram(self, mode=0):
        tmp = mode % 2
        cmd = NVMePassthruCmd()
        cmd.OPCODE = OPCODE.CNEX_VU_COMMAND
        cmd.CDW[15] = 0x2 + tmp
        return self.admin_passthru(cmd)


class Tahoe(NVMe):
    OFFSET_REGISTER = 0x100000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dll = CDLL(os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "dll", 'buf.so')))
        self.dll.nvme_alloc.restype = c_uint64
        vu_class = VUProjectType.from_name(self.__class__.__name__+"VU")
        self.vu_cmd = vu_class(self)

    def read_register(self, addr):
        return self.vu_cmd.get_memory(addr + self.OFFSET_REGISTER)[0]

    def write_register(self, addr, value):
        dptr = (c_uint32 * 128)(value)
        self.vu_cmd.set_memory(addr + self.OFFSET_REGISTER, dptr, length=1)

    def get_average_power_consumption(self, duration=60, delay=1):
        pc = 0
        max_cre = 0
        min_cre = 0
        avg_cre = 0
        for _ in range(duration):
            data = self.vu_cmd.get_power_consumption()
            pc += data[0]
            max_cre += data[1]
            min_cre += data[2]
            avg_cre += data[3]
            sleep(delay)
        return pc/duration, max_cre/duration, min_cre/duration, avg_cre/duration

    def check_security(self, offset, length):
        tmp = self.vu_cmd.get_drive_security_state()
        if length == 1:
            return tmp[offset]
        else:
            sum = 0
            a = tmp[offset:(offset+length)]
            for i in range(length):
                sum = sum + (a[i] << (i * 8))
            return sum

    def get_vendor_uniquelog(self, length, offset):
        dptr = (c_uint8 * 512)()
        self.get_log(dptr, lid=0xDE)
        a = dptr[offset:(offset + length)]
        sum = 0
        for i in range(length):
            sum = sum + (a[i] << (i * 8))
        return sum

    def check_int_type(self):
        return self.vu_cmd.get_int_type()

    def check_data(self, val):
        if val:
            return val
        return ""

    def get_info(self):
        id_ctrl_buffer = Ctype(self.identify_ctrl())
        dev_info = {}
        ssd_config_dic = {}
        drive_life_info_dic = {}
        test_fw_config_dic = {}
        fw_repo = self.check_data(re.findall('http\S+git', id_ctrl_buffer.get('VS'))[0])
        fw_branch_name = self.check_data(re.findall(".*git(.*)commit.*", id_ctrl_buffer.get('VS'))[0])
        fw_private_revision = self.check_data(re.findall('commit (\w+)', id_ctrl_buffer.get('VS'))[0])
        tnvmecap = self.check_data(id_ctrl_buffer.get('TNVMCAP'))
        fw_public_revision = self.check_data(id_ctrl_buffer.get('FR'))
        vid = self.check_data(id_ctrl_buffer.get('VID'))
        drive_sn = self.check_data(id_ctrl_buffer.get('SN'))
        drive_pn = self.check_data(id_ctrl_buffer.get('MN'))
        security_type = "ISE" if self.check_security(2, 1) else "SED"
        security_status = "security enable" if self.check_security(3, 1) else "security disable"
        int_type = self.check_data(self.check_int_type())
        life_cycle_state = self.check_security(16, 4)
        count_grown_defects = self.check_data(self.get_vendor_uniquelog(4, 144))
        count_primary_defects = self.check_data(self.get_vendor_uniquelog(4, 152))
        nand_max_erase_count = self.check_data(self.get_vendor_uniquelog(2, 112))
        nand_min_erase_count = self.check_data(self.get_vendor_uniquelog(2, 96))
        nand_avg_erase_count = self.check_data(self.get_vendor_uniquelog(2, 104))
        ssd_config_dic['drive_sn'] = drive_sn
        ssd_config_dic['drive_pn'] = drive_pn
        ssd_config_dic['vid'] = vid
        ssd_config_dic['drive_tnvmcap'] = tnvmecap
        ssd_config_dic['security_status'] = security_status
        ssd_config_dic['security_type'] = security_type
        ssd_config_dic['int_type'] = int_type
        drive_life_info_dic['life_cycle_state'] = life_cycle_state
        drive_life_info_dic['count_grown_defects'] = count_grown_defects
        drive_life_info_dic['count_primary_defects'] = count_primary_defects
        drive_life_info_dic['nand_max_erase_count'] = nand_max_erase_count
        drive_life_info_dic['nand_min_erase_count'] = nand_min_erase_count
        drive_life_info_dic['nand_avg_erase_count'] = nand_avg_erase_count
        test_fw_config_dic['fw_public_revision'] = fw_public_revision
        test_fw_config_dic['fw_repo'] = fw_repo
        test_fw_config_dic['fw_private_revision'] = fw_private_revision
        test_fw_config_dic['fw_branch_name'] = fw_branch_name
        dev_info['ssd_config_dic'] = ssd_config_dic
        dev_info['drive_life_info_dic'] = drive_life_info_dic
        dev_info['test_fw_config_dic'] = test_fw_config_dic
        return dev_info
