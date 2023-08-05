#!/usr/bin/env python
# coding=utf-8
#pylint: disable=too-many-public-methods,too-many-locals,too-many-arguments,superfluous-parens,import-error,invalid-name,wildcard-import,unused-wildcard-import,missing-docstring
from ctypes import c_uint8, c_uint32
from tool.device.nvme import NVMe
from tool.device.nvme import struct as STRUCT
from tool.device.nvme.struct import FeatureID as Fid
from tool.device.nvme import buf


class Feature(object):
    def __init__(self, dev, fid, dw11=0, nsid=0):
        self.nsid = nsid
        self.fid = fid
        self.dw11 = dw11
        self.dev = NVMe() if dev is None else dev

        self.dword0 = buf.Malloc(length=1, types=c_uint32)
        self.buffer = buf.Malloc(length=4096 * 2, types=c_uint8)
        self.get_cap()
        self.base_values = {}

    def get_cap(self):
        """get capability"""
        cdword0_struct = self.dev.get_features(self.fid, 3, self.dw11)[1]
        cdword0 = cdword0_struct.DWORD
        self.saveable = cdword0 & 0x1
        self.changeable = (cdword0 & 0b100) >> 2
        self.ns_spec = (cdword0 & 0b10) >> 1

    def get_expect_value(self, sel, set_attr):
        """get expect value"""
        if 'save' in set_attr:
            set_sv = set_attr['save']
        else:
            set_sv = 0
        if sel == 0:
            if self.changeable:
                return set_attr
            return self.base_values[0]
        elif sel == 1:
            return self.base_values[1]
        elif sel == 2:
            if (set_sv is 0) or (not self.saveable):
                return self.base_values[2]
            return set_attr
        else:
            print("Not supported SEL in compare mode")
        return False

    def printf(self):
        pass

    def check_attr(self, set_attr, sel):
        """check attribute"""
        expect = self.get_expect_value(sel, set_attr)
        if not expect:
            return expect
        print('actual value:')
        self.printf()
        print('expect value:\n{}'.format(expect))
        return self.compare_field(expect)

    def compare_field(self, expect):
        pass


class Arbitration(Feature):
    """Arbitration base on Feature"""
    def __init__(self, dev=None, nsid=0):
        super(Arbitration, self).__init__(dev, Fid.Arbitration, nsid=nsid)
        self.cfg = self.dword0.convert(STRUCT.Arbitration)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            value = {"hpw": dw0.HPW,
                     "mpw": dw0.MPW,
                     "lpw": dw0.LPW,
                     "ab": dw0.AB}
            self.base_values[i] = value

    def printf(self):
        """print Arbitration"""
        print("---------> get feature Arbitration")
        print(" Namespace:                                 0x{:x}".format(self.nsid))
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" High Priority Weight:                      0x{:x}".format(self.cfg.HPW))
        print(" Medium Priority Weight:                    0x{:x}".format(self.cfg.MPW))
        print(" Low Priority Weight:                       0x{:x}".format(self.cfg.LPW))
        print(" Arbitration Burst:                         0x{:x}".format(self.cfg.AB))

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_arbitration(set_attr['save'], set_attr['ab'], set_attr['lpw'],
                                                set_attr['mpw'], set_attr['hpw'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.HPW == expect['hpw'] and self.cfg.MPW == expect['mpw'] and \
                self.cfg.LPW == expect['lpw'] and self.cfg.AB == expect['ab']:
            return True
        return False


class PowerManagement(Feature):
    """Power Management (Feature Identifier 02h)"""

    def __init__(self, dev=None):
        super(PowerManagement, self).__init__(dev, Fid.PowerManagement)
        self.cfg = self.dword0.convert(STRUCT.PowerManagement)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            value = {"wh": dw0.WH,
                     "ps": dw0.PS}
            self.base_values[i] = value

    def printf(self):
        """print value"""
        print("---------> Get Feature - Power Management")
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" Workload Hint:                             0x{:x}".format(self.cfg.WH))
        print(" Power State:                               0x{:x}".format(self.cfg.PS))

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.WH == expect['wh'] and self.cfg.PS == expect['ps']:
            return True
        return False

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_power_management(set_attr['save'],
                                                     set_attr['ps'], set_attr['wh'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret


class LBARangeType(Feature):
    """LBA Range Type (Feature Identifier 03h), (Optional)"""

    def __init__(self, dev=None, prpo1=0, prpo2=0, index=0):
        super(LBARangeType, self).__init__(dev, Fid.LBARangeType, prpo1, prpo2)
        self.cfg = self.dword0.convert(STRUCT.LBARangeType)
        self.entry = self.buffer.convert(STRUCT.LBARangeTypeEntry, index=index)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            value = {"TYPE": self.entry.TYPE, "ATTR": self.entry.ATTR, "SLBA": self.entry.SLBA,
                     "NLB": self.entry.NLB, "GUID": self.entry.GUID.LOW}
            self.base_values[i] = value
            print(self.base_values)

    def printf(self):
        """print value"""
        print("---------> get feature LBA Range Type")
        print(" Saveable:                    0x{:x}".format(self.saveable))
        print(" Changeable:                  0x{:x}".format(self.changeable))
        print(" Namespace specific:          0x{:x}".format(self.ns_spec))
        print(" Type:                        0x{:x}".format(self.entry.TYPE))
        print(" Attributes:                  0x{:x}".format(self.entry.ATTR))
        print(" Starting LBA:                0x{:x}".format(self.entry.SLBA))
        print(" Number of Logical Blocks:    0x{:x}".format(self.entry.NLB))
        print(" Unique Identifier:           0x{!r}".format(self.entry.GUID.LOW))

    def test_values(self, set_attr):
        """test values"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        lrt = [{'TYPE': 3, 'ATTR': 2, 'SLBA': 0x1234, 'NLB': 0x321, 'GUID': 0x2}]
        ret = self.dev.set_features_lba_range_type(lrt, set_attr['save'])
        for i in range(3):
            self.entry = self.dev.get_features(self.fid, i, self.dw11)[2][0]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.entry.TYPE == expect['TYPE'] and self.entry.ATTR == expect['ATTR'] and \
                self.entry.SLBA == expect['SLBA'] and self.entry.NLB == expect['NLB'] and \
                self.entry.GUID.LOW == expect['GUID']:
            return True
        return False


class TemperatureThreshold(Feature):
    """TemperatureThreshold base on Feature"""

    def __init__(self, dev=None):
        super(TemperatureThreshold, self).__init__(dev, Fid.TemperatureThreshold, 0, 0)
        self.cfg = self.dword0.convert(STRUCT.TemperatureThreshold)
        self.set_attr = None
        self.get_current_value()

    def printf(self):
        """print value"""
        print("---------> get feature Temperature Threshold")
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print("Threshold Type Select:                      0x{:x}".format(self.cfg.THSEL))
        print("Threshold Temperature Select:               0x{:x}".format(self.cfg.TMPSEL))
        print("Temperature Threshold:                      0x{:x}".format(self.cfg.TMPTH))

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            value = {"thsel": dw0.THSEL,
                     "tmpsel": dw0.TMPSEL,
                     "tmpth": dw0.TMPTH}
            self.base_values[i] = value

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_temperature_threshold(set_attr['save'], set_attr['tmpth'],
                                                          set_attr['tmpsel'], set_attr['thsel'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.THSEL == expect['thsel'] and self.cfg.TMPSEL == expect['tmpsel'] and \
                self.cfg.TMPTH == expect['tmpth']:
            return True
        return False


class ErrorRecovery(Feature):
    """ErrorRecovery base on Feature"""

    def __init__(self, dev=None):
        super(ErrorRecovery, self).__init__(dev, Fid.ErrorRecovery, 0, 0)
        self.cfg = self.dword0.convert(STRUCT.ErrorRecovery)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            value = {"tler": dw0.TLER,
                     "dulbe": dw0.DULBE}
            self.base_values[i] = value
            print(self.base_values)

    def printf(self):
        """print value"""
        print(" Saveable:               0x{:x}".format(self.saveable))
        print(" Changeable:             0x{:x}".format(self.changeable))
        print(" Namespace specific:     0x{:x}".format(self.ns_spec))
        print(" Deallocated or Unwritten Logical Block Error Enable: 0x{:x}".format(self.cfg.DULBE))
        print(" Time Limited Error Recovery:  0x{:x}".format(self.cfg.TLER))

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_error_recovery(set_attr['save'],
                                                   set_attr['tler'], set_attr['dulbe'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.DULBE == expect['dulbe'] and self.cfg.TLER == expect['tler']:
            return True
        return False


class VolatileWriteCache(Feature):
    """VolatileWriteCache base on Feature"""

    def __init__(self, dev=None):
        super(VolatileWriteCache, self).__init__(dev, Fid.VolatileWriteCache, 0, 0)
        self.cfg = self.dword0.convert(STRUCT.VolatileWriteCache)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            valuse = {"wce": dw0.WCE}
            self.base_values[i] = valuse

    def printf(self):
        """print value"""
        print("---------> get feature Volatile WriteCache")
        print(" Saveable:             0x{:x}".format(self.saveable))
        print(" Changeable:           0x{:x}".format(self.changeable))
        print(" Namespace specific:   0x{:x}".format(self.ns_spec))
        print(" Volatile Write Cache Enable:     0x{:x}".format(self.cfg.WCE))

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_volatile_write_cache(set_attr['save'], set_attr['wce'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.WCE == expect['wce']:
            return True
        return False


class InterruptCoalescing(Feature):
    """InterruptCoalescing"""

    def __init__(self, dev=None):
        super(InterruptCoalescing, self).__init__(dev, Fid.InterruptCoalescing, 0, 0)
        self.cfg = self.dword0.convert(STRUCT.InterruptCoalescing)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            values = {"time": dw0.TIME, "thr": dw0.THR}
            self.base_values[i] = values
            print(self.base_values)

    def printf(self):
        """print value"""
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" Aggregation Time:                          0x{:x}".format(self.cfg.TIME))
        print(" Aggregation Threshold:                     0x{:x}".format(self.cfg.THR))

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_interrupt_coalescing(set_attr['save'],
                                                         set_attr['thr'], set_attr['time'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.THR == expect['thr'] and self.cfg.TIME == expect['time']:
            return True
        return False


class InterruptVectorConfiguration(Feature):
    """InterruptVectorConfiguration"""

    def __init__(self, dev=None):
        super(InterruptVectorConfiguration, self).__init__(dev, Fid.InterruptVectorConfiguration,
                                                           0, 0)
        self.cfg = self.dword0.convert(STRUCT.InterruptVectorConfiguration)
        self.get_current_value()

    def printf(self):
        """print value"""
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" Coalescing Disable:                        0x{:x}".format(self.cfg.CD))
        print(" Interrupt Vector:                          0x{:x}".format(self.cfg.IV))

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            value = {"cd": dw0.CD, "iv": dw0.IV}
            self.base_values[i] = value
            print(self.base_values)

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_interrupt_vector_configuration(set_attr['save'],
                                                                   set_attr['iv'], set_attr['cd'])
        for i in range(3):
            iv = [0x4, 0x9, 0x10]
            self.dw11 = iv[i]
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.CD == expect['cd'] and self.cfg.IV == expect['iv']:
            return True
        return False


class WriteAtomicity(Feature):
    """WriteAtomicity"""

    def __init__(self, dev=None):
        super(WriteAtomicity, self).__init__(dev, Fid.WriteAtomicityNormal, 0, 0)
        self.cfg = self.dword0.convert(STRUCT.WriteAtomicityNormal)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            value = {"dn": dw0.DN}
            self.base_values[i] = value
            print(self.base_values)

    def printf(self):
        """print value"""
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" Disable Normal:                            0x{:x}".format(self.cfg.DN))

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_write_atomicity_normal(set_attr['save'], set_attr['dn'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.DN == expect['dn']:
            return True
        return False


class AsynchronousEventConfiguration(Feature):
    """AsynchronousEventConfiguration"""

    def __init__(self, dev=None):
        super(AsynchronousEventConfiguration, self).__init__(dev,\
                                        Fid.AsynchronousEventConfiguration, 0, 0)
        self.cfg = self.dword0.convert(STRUCT.AsynchronousEventConfiguration)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            value = {"fan": dw0.FAN,
                     "nan": dw0.NAN,
                     "shcw": dw0.SHCW,
                     "tln": dw0.TLN}
            self.base_values[i] = value

    def printf(self):
        """print value"""
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" Firmware Activation Notices:               0x{:x}".format(self.cfg.FAN))
        print(" Namespace Attribute Notices:               0x{:x}".format(self.cfg.NAN))
        print(" SMART / Health Critical Warnings:          0x{:x}".format(self.cfg.SHCW))

    def test_values(self, set_attr):
        """test_value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_asynchronous_event_configuration(set_attr['save'], \
                set_attr['shcw'], set_attr['nan'], set_attr['fan'], set_attr['tln'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.FAN == expect['fan'] and self.cfg.NAN == expect['nan'] and \
                self.cfg.SHCW == expect['shcw'] and self.cfg.TLN == expect['tln']:
            return True
        return False


class AutonomousPowerStateTransition(Feature):
    """Autonomous Power State Transition"""

    def __init__(self, dev=None):
        super(AutonomousPowerStateTransition, self).__init__(dev, Fid.AutonomousPowerStateTransition, 0, 0)
        self.entry = self.buffer.convert(STRUCT.AutonomousPowerStateTransitionEntry)
        self.cfg = self.dword0.convert(STRUCT.AutonomousPowerStateTransition)
        self.get_current_value()

    def printf(self):
        """print value"""
        print(" Saveable:                                   0x{:x}".format(self.saveable))
        print(" Changeable:                                 0x{:x}".format(self.changeable))
        print(" Namespace specific:                         0x{:x}".format(self.ns_spec))
        print(" Autonomous Power State Transition Enable:   0x{:x}".format(self.cfg.APSTE))
        print(" Idle Time Prior to Transition:              0x{:x}".format(self.entry.ITPT))
        print(" Idle Transition Power State:                0x{:x}".format(self.entry.ITPS))

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            valuse = {"apste": dw0.APSTE}
            self.base_values[i] = valuse

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.APSTE == expect['apste']:
            return True
        return False

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_autonomous_power_state_transition(set_attr['save'], set_attr['apste'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret


class SoftwareProgressMarker(Feature):
    """SoftwareProgressMarker base on Feature"""

    def __init__(self, dev=None):
        super(SoftwareProgressMarker, self).__init__(dev, Fid.SoftwareProgressMarker, 0, 0)
        self.cfg = self.dword0.convert(STRUCT.SoftwareProgressMarker)
        self.get_current_value()

    def printf(self):
        """print value"""
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" Pre-boot Software Load Count:              0x{:x}".format(self.cfg.PBSLC))

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            value = {"pbslc": dw0.PBSLC}
            self.base_values[i] = value
            print(self.base_values[i])

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_software_progress_marker(set_attr['save'], set_attr['pbslc'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.PBSLC == expect['pbslc']:
            return True
        return False


class HostIdentifier(Feature):
    """Host Identifier ONLY 8 bytes data structure"""

    def __init__(self, dev=None):
        super(HostIdentifier, self).__init__(dev, Fid.HostIdentifier, 0, 0)
        self.entry = self.buffer.convert(STRUCT.HostIdentifierEntry)
        self.cfg = self.dword0.convert(STRUCT.HostIdentifier)
        self.get_current_value()

    def printf(self):
        """print value"""
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" Enable Host Identifier:                    0x{:x}".format(self.cfg.EXHID))
        print(" Host Identifier Low 64:                    0x{:x}".format(self.entry.HOSTIDL))
        print(" Host Identifier High 64:                   0x{:x}".format(self.entry.HOSTIDH))

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            value = {"exhid": dw0.EXHID,
                     "hostidl": self.entry.HOSTIDL,
                     "hostidh": self.entry.HOSTIDH, }
            self.base_values[i] = value
            print(self.base_values[i], "WWWW")

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_host_identifier(set_attr['exhid'], set_attr['hostidl'],
                                                    set_attr['hostidh'], set_attr['save'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.entry.HOSTIDL == expect['hostidl'] and self.entry.HOSTIDH == expect['hostidh']:
            return True
        return False


class Timestamp(Feature):
    """ReservationPersistence"""

    def __init__(self, dev=None):
        super(Timestamp, self).__init__(dev, Fid.Timestamp, 0, 0)
        self.entry = self.buffer.convert(STRUCT.Timestamp)
        self.cfg = self.dword0.convert(STRUCT.Timestamp)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            value = {"timestamp": self.entry.TIMESTAMP,
                     "synch": self.entry.SYNCH,
                     "to": self.entry.TO}
            self.base_values[i] = value
            print(self.base_values[i])

    def printf(self):
        """print value"""
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" Timestamp:                                 0x{:x}".format(self.entry.TIMESTAMP))
        print(" Synch:                                     0x{:x}".format(self.entry.SYNCH))
        print(" Timestamp Origin:                          0x{:x}".format(self.entry.TO))

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_timestamp(set_attr['timestamp'], set_attr['save'])
        for i in range(3):
            self.dword0 = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def get_expect_value(self, sel, set_attr):
        """get expect value"""
        if sel in (0, 1, 2):
            value = self.base_values[0]
        else:
            print("Not supported SEL in compare mode")
            value = False
        return value

    def compare_field(self, expect):
        """compare_field"""
        if self.entry.TIMESTAMP == expect['timestamp'] and self.entry.SYNCH == expect['synch'] and \
                self.entry.TO == expect['to']:
            return True
        return False


class HostControlledThermalManagement(Feature):
    """KeepAliveTimer"""

    def __init__(self, dev=None):
        super(HostControlledThermalManagement, self).__init__(dev, \
                            Fid.HostControlledThermalManagement, 0, 0)
        self.cfg = self.dword0.convert(STRUCT.HostControlledThermalManagement)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            print("-----------sel : %d" % i)
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            valuse = {"tmt1": dw0.TMT1,
                      "tmt2": dw0.TMT2}
            self.base_values[i] = valuse

    def printf(self):
        """print value"""
        print("---------> get feature Number of Queues")
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" Thermal Management Temperature 1:          0x{:x}".format(self.cfg.TMT1))
        print(" Thermal Management Temperature 2:          0x{:x}".format(self.cfg.TMT2))

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.TMT1 == expect['tmt1'] and self.cfg.TMT2 == expect['tmt2']:
            return True
        return False

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_host_controlled_thermal_management(set_attr['save'], \
                                set_attr['tmt2'], set_attr['tmt1'])
        for i in range(3):
            self.dword0 = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret


class NonOperationalPowerStateConfig(Feature):
    """NonOperationalPowerStateConfig"""

    def __init__(self, dev=None):
        super(NonOperationalPowerStateConfig, self).__init__(dev, Fid.NonOperationalPowerStateConfig, 0, 0)
        self.cfg = self.dword0.convert(STRUCT.NonOperationalPowerStateConfig)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(4):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            valuse = {"NOPPME": dw0.NOPPME}
            self.base_values[i] = valuse

    def printf(self):
        """print value"""
        print("---------> get feature Number of Queues")
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" Non-Operational Power State Permissive Mode Enable: 0x{:x}".format(self.cfg.NOPPME))

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.NOPPME == expect['NOPPME']:
            return True
        return False

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_nonoperational_power_state_config(set_attr['save'], set_attr['noppme'])
        for i in range(3):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret


class HostMemoryBuffer(Feature):
    """HostMemoryBuffer"""
    def __init__(self, dev=None):
        super(HostMemoryBuffer, self).__init__(dev, Fid.HostMemoryBuffer, 0, 0)
        self.cfg = self.dword0.convert(STRUCT.HostMemoryBuffer)
        self.get_current_value()

    def get_current_value(self):
        """get current value"""
        for i in range(2):
            _, dw0, _ = self.dev.get_features(self.fid, i, self.dw11)
            valuse = {"EHM": dw0.EHM,
                      "MR":  dw0.MR}
            self.base_values[i] = valuse

    def printf(self):
        """print value"""
        print("---------> get feature Number of Queues")
        print(" Saveable:                                  0x{:x}".format(self.saveable))
        print(" Changeable:                                0x{:x}".format(self.changeable))
        print(" Namespace specific:                        0x{:x}".format(self.ns_spec))
        print(" Enable Host Memory: 0x{:x}".format(self.cfg.EHM))
        print(" Memory Return: 0x{:x}".format(self.cfg.MR))

    def test_values(self, set_attr):
        """test value"""
        return self.set_and_get_all_sel(set_attr)

    def set_and_get_all_sel(self, set_attr):
        """set_and_get_all_sel"""
        ret = self.dev.set_features_host_memory_buffer(set_attr['save'], \
            set_attr['ehm'], set_attr['mr'], set_attr['esize'], set_attr['hdmlec'])
        for i in range(2):
            self.cfg = self.dev.get_features(self.fid, i, self.dw11)[1]
            ret = self.check_attr(set_attr, i)
            if ret is False:
                print("***********************Test failed: select is {}".format(i))
            else:
                print("***********************Test Passed: select is {}".format(i))
        return ret

    def compare_field(self, expect):
        """compare_field"""
        if self.cfg.EHM == expect['EHM'] and self.cfg.MR == expect['MR']:
            return True
        return False
