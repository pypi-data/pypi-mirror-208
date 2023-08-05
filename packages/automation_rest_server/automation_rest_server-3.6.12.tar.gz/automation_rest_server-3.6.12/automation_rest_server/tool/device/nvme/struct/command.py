#!/usr/bin/env python
# pylint: disable=superfluous-parens,missing-docstring,too-few-public-methods
"""
Created on Apr 19, 2019

@author: yyang
"""
from ctypes import Structure, c_uint8, c_uint16, c_uint32, c_uint64, Union

from tool.device.nvme.ctype import Uint128


class OPCODE(object):
    DELETE_IO_SQ = 0x00
    CREATE_IO_SQ = 0x01
    GET_LOG_PAGE = 0x02
    DELETE_IO_CQ = 0x04
    CREATE_IO_CQ = 0x05
    IDENTIFY = 0x06
    ABORT = 0x08
    SET_FEATURES = 0x09
    GET_FEATURES = 0x0A
    ASYNC_EVENT_REQUEST = 0x0C
    NAMESPACE_MGT = 0x0D
    FIRMWARE_COMMIT = 0x10
    FIRMWARE_DOWNLOAD = 0x11
    DEVICE_SELF_TEST = 0x14
    NAMESPACE_ATTACH = 0x15
    DIRECTIVE_SEND = 0x19
    DIRECTIVE_RECEIVE = 0x1A
    VIRT_MANAGEMENT = 0x1C
    NVME_MI_SEND = 0x1D
    NVME_MI_RECEIVE = 0x1E
    FORMAT_NVM = 0x80
    SECURITY_SEND = 0x81
    SECURITY_RECV = 0x82
    SANITIZE = 0X84

    FLUSH = 0x00
    WRITE = 0x01
    READ = 0x02
    WRITE_UNCORRECTABLE = 0x04
    COMPARE = 0x05
    WRITE_ZEROES = 0x08
    DATASET_MGT = 0x09
    RESERVATION_REGISTER = 0x0D
    RESERVATION_REPORT = 0x0E
    RESERVATION_ACQUIRE = 0x11
    RESERVATION_RELEASE = 0x15

    CNEX_WRITE_MEM = 0x99
    CNEX_READ_MEM = 0x9A
    CNEX_CLEAR_GBB = 0xC3
    CNEX_VU_COMMAND = 0xC4

    AGING_MF = 0xEC

    KNUCKLE_VU_SUM = 0xEC
    KNUCKLE_VU_FW = 0xED
    KNUCKLE_VU_GET = 0xEE
    KNUCKLE_VU_NON = 0xEC
    KNUCKLE_VU_WR = 0xED
    KNUCKLE_VU_RD = 0xEE
    KNUCKLE_VU_RATE_LI = 0xEF

    KNUCKLE_VU_SUB_LVM = 0x3
    KNUCKLE_VU_SUB_QUEUE_STATE = 0x3

    ADMIN = {
        0x0: 'Delete IO SQ',
        0x1: 'Create IO SQ',
        0x2: 'Get Log Page',
        0x4: 'Delete IO CQ',
        0x5: 'Create IO CQ',
        0x6: 'Identify',
        0x8: 'Abort',
        0x9: 'Set Features',
        0xa: 'Get Features',
        0xc: 'Asynchronous Event Request',
        0xd: 'Namespace Management',
        0x10: 'Firmware_Commit',
        0x11: 'Firmware Image_Download',
        0x14: 'Device Self-test',
        0x15: 'Namespace Attachment',
        0x18: 'Keep Alive',
        0x19: 'Directive Send',
        0x1a: 'Directive Receive',
        0x1c: 'Virtualization Management',
        0x1d: 'NVMe-MI Send',
        0x1e: 'NVMe-MI Receive',
        0x7c: 'Doorbell Buffer Config',
        0x80: 'Format NVM',
        0x81: 'Security Send',
        0x82: 'Security Receive',
        0x84: 'Sanitize',
    }

    IO = {
        0x0: 'Flush',
        0x1: 'Write',
        0x2: 'Read',
        0x4: 'Write Uncorrectable',
        0x5: 'Compare',
        0x8: 'Write Zeroes',
        0x9: 'Dataset Management',
        0xd: 'Reservation Register',
        0xe: 'Reservation Report',
        0x11: 'Reservation Acquire',
        0x15: 'Reservation Release',
        0x99: 'CNEX Write Memory',
        0x9a: 'CNEX Read Memory'
    }


class DebugOPCODE(object):
    ASYNC_TRACE = 0x00
    GET_CQE = 0x01
    GET_SQE = 0x02


class LVMOPCODE(object):
    START_TRACK_IO = 0x1
    START_TRACK_MEM = 0x2
    STOP_TRACK = 0x3
    STOP_MWR = 0x4


class LVMTenantID(object):
    PHR = 0x0
    LVM_IO = 0x1
    LVM_MWR = 0x2
    VF1_IO = 0x10
    VF1_MWR = 0x11
    VF2_IO = 0x20
    VF2_MWR = 0x21
    CIAI = 0x3
    INVALID = 0x3f


class PNVMeDebug(Structure):
    _pack_ = 1
    _fields_ = [
        ('OPCODE', c_uint32),
        ('RSV', c_uint32),
        ('DATA', c_uint64),
    ]


class PNVMeIOCmd(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('OPCODE', c_uint8),
            ('FLAGS', c_uint8),
            ('CID', c_uint16),
            ('NSID', c_uint32),
            ('CDW2', c_uint32),
            ('CDW3', c_uint32),
            ('META', c_uint64),
            ('PRP1', c_uint64),
            ('PRP2', c_uint64),
            ('SLBA', c_uint64),
            ('NLB', c_uint16),
            ('CTRL', c_uint16),
            ('DSMGMT', c_uint8),
            ('QID', c_uint8),
            ('DIR', c_uint16),
            ('REFTAG', c_uint32),
            ('APPTAG', c_uint16),
            ('APPMASK', c_uint16),
        ]

    class CDWS(Structure):
        _pack_ = 1
        _fields_ = [
            ('CDW', c_uint32 * 16),
        ]

    _anonymous_ = ('CDWS', 'BITS')
    _fields_ = [
        ('CDWS', CDWS),
        ('BITS', BITS),
    ]


class NVMeUserIO(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('OPCODE', c_uint8),
            ('FLAGS', c_uint8),
            ('CONTROL', c_uint16),
            ('NBLOCKS', c_uint16),
            ('RSV', c_uint16),
            ('META', c_uint64),
            ('DATA', c_uint64),
            ('SLBA', c_uint64),
            ('DSMGMT', c_uint32),
            ('REFTAG', c_uint32),
            ('APPTAG', c_uint16),
            ('APPMASK', c_uint16),
        ]

    class CDWS(Structure):
        _pack_ = 1
        _fields_ = [
            ('CDW', c_uint32 * 12),
        ]

    _anonymous_ = ('CDWS', 'BITS')
    _fields_ = [
        ('CDWS', CDWS),
        ('BITS', BITS),
    ]


class NVMeSGLIO(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('OPCODE', c_uint8),
            ('FLAGS', c_uint8),
            ('CID', c_uint16),
            ('NSID', c_uint32),
            ('CDW2', c_uint32*2),
            ('META', c_uint64),
            ('PRP1', c_uint64),
            ('PRP2', c_uint64),
            ('SLBA', c_uint64),
            ('NLB', c_uint16),
            ('CTRL', c_uint16),
            ('DSMGMT', c_uint8),
            ('QID', c_uint8),
            ('DIRECTIVE_SPEC', c_uint16),
            ('REFTAG', c_uint32),
            ('APPTAG', c_uint16),
            ('APPMASK', c_uint16),
            ('DATA_OFF', c_uint32),
            ('META_OFF', c_uint32),
            ('DATA_DES_NUM', c_uint64),
            ('META_DES_NUM', c_uint64),
            ('SGL_DATA_PTR', c_uint64),
            ('SGL_META_PTR', c_uint64),
        ]

    class CDWS(Structure):
        _pack_ = 1
        _fields_ = [
            ('CDW', c_uint32 * 26),
        ]

    _anonymous_ = ('CDWS', 'BITS')
    _fields_ = [
        ('CDWS', CDWS),
        ('BITS', BITS),
    ]


class NVMePassthruCmd(Union):
    """
    Take Care: different with SQE!
    cdw8 is metadata_len and cdw9 is data_len
    Add cdw16: timeout
    Add cdw17: dword0 of CQE
    """

    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('OPCODE', c_uint8),
            ('FLAGS', c_uint8),
            ('RSV', c_uint16),
            ('NSID', c_uint32),
            ('CDW2', c_uint32),
            ('CDW3', c_uint32),
            ('META', c_uint64),
            ('DATA', c_uint64),
            ('META_LEN', c_uint32),
            ('DATA_LEN', c_uint32),
            ('CDW10', c_uint32),
            ('CDW11', c_uint32),
            ('CDW12', c_uint32),
            ('CDW13', c_uint32),
            ('CDW14', c_uint32),
            ('CDW15', c_uint32),
            ('TIMEOUT', c_uint32),
            ('RESULT', c_uint32),
        ]

    class CDWS(Structure):
        _pack_ = 1
        _fields_ = [
            ('CDW', c_uint32 * 18),
        ]

    _anonymous_ = ('CDWS', 'BITS')
    _fields_ = [
        ('CDWS', CDWS),
        ('BITS', BITS)
    ]


class RWDword12(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('NLB', c_uint16),  # Number Of Logical Blocks (NLB)
            ('RSV0', c_uint16, 4),
            ('DTYPE', c_uint16, 4),  # Directive Type (DTYPE)
            ('RSV1', c_uint16, 1),
            ('DEAC', c_uint16, 1),  # Deallocate (DEAC)
            ('PRINFO', c_uint16, 4),  # Protection Information (PRINFO)
            ('FUA', c_uint16, 1),  # Force Unit Access (FUA)
            ('LR', c_uint16, 1),  # Limited Retry (LR)
        ]

    class WORD(Structure):
        _pack_ = 1
        _fields_ = [
            ('NBLOCKS', c_uint16),
            ('CONTROL', c_uint16),
        ]

    _anonymous_ = ('BITS', 'WORD')
    _fields_ = [
        ('DWORD', c_uint32),
        ('WORD', WORD),
        ('BITS', BITS),
    ]


class RWDword13(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('DSM', c_uint8),  # Dataset Management (DSM)
            ('RSV', c_uint8),
            ('DSPEC', c_uint16),  # Directive Specific (DSPEC)
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class ReservationAcquire(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('RACQA', c_uint32, 3),  # Reservation Acquire Action (RACQA)
            ('IEKEY', c_uint32, 1),  # Ignore Existing Key (IEKEY)
            ('RSV0', c_uint32, 4),
            ('RTYPE', c_uint32, 8),  # Reservation Type (RTYPE)
            ('RSV1', c_uint32, 16),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class ReservationAcquireDataStructure(Structure):
    _pack_ = 1
    _fields_ = [
        ('CRKEY', c_uint64),  # Current Reservation Key (CRKEY)
        ('PRKEY', c_uint64),  # Preempt Reservation Key (PRKEY)
    ]


class ReservationRegister(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('RREGA', c_uint32, 3),  # Reservation Register Action (RREGA)
            ('IEKEY', c_uint32, 1),  # Ignore Existing Key (IEKEY)
            ('RSV0', c_uint32, 26),
            ('CPTPL', c_uint32, 2),  # Change Persist Through Power Loss State (CPTPL)
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class ReservationRegisterDataStructure(Structure):
    _pack_ = 1
    _fields_ = [
        ('CRKEY', c_uint64),  # Current Reservation Key (CRKEY)
        ('NRKEY', c_uint64),  # New Reservation Key (NRKEY)
    ]


class ReservationRelease(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('RRELA', c_uint32, 3),  # Reservation Release Action (RRELA)
            ('IEKEY', c_uint32, 1),  # Ignore Existing Key (IEKEY)
            ('RSV0', c_uint32, 4),
            ('RTYPE', c_uint32, 8),  # Reservation Type (RTYPE)
            ('RSV1', c_uint32, 16),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class ReservationReleaseDataStructure(Structure):
    _pack_ = 1
    _fields_ = [
        ('CRKEY', c_uint64),  # Current Reservation Key (CRKEY)
    ]


class RegisteredControllerDataStructure(Structure):
    _pack_ = 1
    _fields_ = [
        ('CNTLID', c_uint16),  # Controller ID (CNTLID)
        ('RCSTS', c_uint8),  # Reservation Status (RCSTS)
        ('RSV0', c_uint8 * 5),
        ('HOSTID', c_uint64),  # Host Identifier (HOSTID)
        ('RKEY', c_uint64),  # Reservation Key (RKEY)
    ]


class ReservationStatusDataStructure(Structure):
    _pack_ = 1
    _fields_ = [
        ('GEN', c_uint32),  # Generation (GEN)
        ('RTYPE', c_uint8),  # Reservation Type (RTYPE)
        ('REGCTL', c_uint16),  # Number of Registered Controllers (REGCTL)
        ('RSV0', c_uint16),
        ('PTPLS', c_uint8),  # Persist Through Power Loss State (PTPLS)
        ('RSV1', c_uint8 * 14),
        ('RCDS', RegisteredControllerDataStructure * 16),  # Registered Controller Data Structure
    ]


class RegisteredControllerExtendedDataStructure(Structure):
    _pack_ = 1
    _fields_ = [
        ('CNTLID', c_uint16),  # Controller ID (CNTLID)
        ('RCSTS', c_uint8),  # Reservation Status (RCSTS)
        ('RSV0', c_uint8 * 5),
        ('RKEY', c_uint64),  # Reservation Key (RKEY)
        ('HOSTID', Uint128),  # Host Identifier (HOSTID)
        ('RSV1', c_uint8 * 32),
    ]


class ReservationStatusExtendedDataStructure(Structure):
    _pack_ = 1
    _fields_ = [
        ('GEN', c_uint32),  # Generation (GEN)
        ('RTYPE', c_uint8),  # Reservation Type (RTYPE)
        ('REGCTL', c_uint16),  # Number of Registered Controllers (REGCTL)
        ('RSV0', c_uint16),
        ('PTPLS', c_uint8),  # Persist Through Power Loss State (PTPLS)
        ('RSV1', c_uint8 * 54),  # Reservation Type (RTYPE)
        ('RCEDS', RegisteredControllerExtendedDataStructure * 16),  # Registered Controller Extended Data Structure
    ]


class CreateIOCQDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('QID', c_uint32, 16),  # Queue Identifier (QID)
            ('QSIZE', c_uint32, 16),  # Queue Size (QSIZE)
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class CreateIOCQDword11(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('PC', c_uint32, 1),  # Physically Contiguous (PC)
            ('IEN', c_uint32, 1),  # Interrupts Enabled (IEN)
            ('RSV', c_uint32, 14),
            ('IV', c_uint32, 16),  # Interrupt Vector (IV)
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class CreateIOSQDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('QUD', c_uint32, 16),  # Queue Identifier (QID)
            ('QSIZE', c_uint32, 16),  # Queue Size (QSIZE)
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class CreateIOSQDword11(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('PC', c_uint32, 1),  # Physically Contiguous (PC)
            ('QPRIO', c_uint32, 2),  # Queue Priority (QPRIO)
            ('RSV', c_uint32, 13),
            ('CQID', c_uint32, 16),  # Completion Queue Identifier (CQID)
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class DeleteIOCQDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('QID', c_uint32, 16),  # Queue Identifier (QID)
            ('RSV', c_uint32, 16),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class DeleteIOSQDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('QID', c_uint32, 16),  # Queue Identifier (QID)
            ('RSV', c_uint32, 16),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class DeviceSelfTest(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('STC', c_uint32, 4),  # Self-test Code (STC)
            ('RSV', c_uint32, 28),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class DirectiveDW11(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('DOPER', c_uint32, 8),  # Directive Operation (DOPER)
            ('DTYPE', c_uint32, 8),  # Directive Type (DTYPE)
            ('DSPEC', c_uint32, 16),  # Directive Specific (DSPEC)
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class NVMeMIDW10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('NMSP0', c_uint32, 8),  # NVMe-MI Specific 0 (NMSP0)
            ('RSV', c_uint32, 24),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class FWCommitDW10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('FS', c_uint32, 3),  # Firmware Slot (FS)
            ('CA', c_uint32, 3),  # Commit Action (CA)
            ('RSV', c_uint32, 25),
            ('BPID', c_uint32, 1),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class FormatDword10(Union):
    """
    The Format NVM command uses the Command Dword 10 field.
    All other command specific fields are reserved.
    """

    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('LBAF', c_uint32, 4),  # LBA Format (LBAF)
            ('MSET', c_uint32, 1),  # Metadata Settings (MSET)
            ('PIF', c_uint32, 3),  # Protection Information (PIF)
            ('PIL', c_uint32, 1),  # Protection Information Location (PIL)
            ('SES', c_uint32, 3),  # Secure Erase Settings (SES)
            ('RSV', c_uint32, 20),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class AbortDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('SQID', c_uint32, 16),
            ('CID', c_uint32, 16),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class IdentifyDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('CNS', c_uint32, 8),
            ('RSV', c_uint32, 8),
            ('CNTID', c_uint32, 16),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class GetFeaturesDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('FID', c_uint32, 8),
            ('SEL', c_uint32, 3),
            ('RSV', c_uint32, 21),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class SetFeaturesDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('FID', c_uint32, 8),
            ('RSV', c_uint32, 23),
            ('SV', c_uint32, 1),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class AttachNSDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('SEL', c_uint32, 4),
            ('RSV', c_uint32, 28),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class SanitizeDW10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('SANACT', c_uint32, 3),  # Sanitize Action
            ('AUSE', c_uint32, 1),  # Allow Unrestricted Sanitize Exit
            ('OWPASS', c_uint32, 4),  # Overwrite Pass Count
            ('OIPBP', c_uint32, 1),  # Overwrite Invert Pattern Between Passes
            ('NDAS', c_uint32, 1),  # No Deallocate After Sanitize
            ('RSV', c_uint32, 22),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class SanitizeDW11(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('OVRPAT', c_uint32, 32),  # Overwrite Pattern
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class CompareDword15(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('ELBAT', c_uint32, 16),
            ('ELBATM', c_uint32, 16),

        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class DsmDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('NR', c_uint32, 8),  # Number of Ranges (NR)
            ('RSV', c_uint32, 24)
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class DsmDword11(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('IDR', c_uint32, 1),
            ('IDW', c_uint32, 1),
            ('AD', c_uint32, 1),
            ('RSV', c_uint32, 29)
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class NamespaceManagementDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('SEL', c_uint32, 4),
            ('RSV', c_uint32, 28)
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class SecurityReceiveDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('NSSF', c_uint32, 8),
            ('SPSP0', c_uint32, 8),
            ('SPSP1', c_uint32, 8),
            ('SECP', c_uint32, 8),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class SecuritySendDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('NSSF', c_uint32, 8),
            ('SPSP0', c_uint32, 8),
            ('SPSP1', c_uint32, 8),
            ('SECP', c_uint32, 8),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class GetLogPagDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('LID', c_uint32, 8),
            ('LSP', c_uint32, 4),  # Log Specific Field (LSP)
            ('RSV0', c_uint32, 3),
            ('RAE', c_uint32, 1),  # Retain Asynchronous Event (RAE)
            ('NUMDL', c_uint32, 16),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class GetLogPagDword11(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('NUMDU', c_uint32, 16),
            ('RSV', c_uint32, 16),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class GetLogPagDword12(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('LPOL', c_uint32, 32),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class GetLogPagDword13(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('LPOU', c_uint32, 32),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class VirtualizationManagementDword10(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('ACT', c_uint32, 4),
            ('RSV0', c_uint32, 4),
            ('RT', c_uint32, 3),
            ('RSV1', c_uint32, 5),
            ('CNTLID', c_uint32, 16),

        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class RateLimitsDword0(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('OPC', c_uint32, 8),
            ('FUSE', c_uint32, 2),
            ('RSV0', c_uint32, 4),
            ('PSDT', c_uint32, 2),
            ('CID', c_uint32, 16),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class RateLimitsDword11(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('IOR_OVERFLOW_CTR', c_uint32, 16),
            ('IOW_OVERFLOW_CTR', c_uint32, 16),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class VirtualizationManagementDword11(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('NR', c_uint32, 16),
            ('RSV0', c_uint32, 16),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class NamespaceManagementDataStructure(Structure):
    _pack_ = 1
    _fields_ = [
        ('NSZE', c_uint64),
        ('NCAP', c_uint64),
        ('RSV0', c_uint8 * 10),
        ('FLBAS', c_uint8),
        ('RSV1', c_uint16),
        ('DPS', c_uint8),
        ('NMIC', c_uint8),
        ('RSV2', c_uint8 * 4065)
    ]


class DatasetManagementContextAttributes(Structure):
    _pack_ = 1
    _fields_ = [
        ('AF', c_uint32, 4),
        ('AL', c_uint32, 2),
        ('RSV0', c_uint32, 2),
        ('SR', c_uint32, 1),
        ('SW', c_uint32, 1),
        ('WP', c_uint32, 1),
        ('RSV1', c_uint32, 13),
        ('CAS', c_uint32, 8),
    ]

class DebugInfo(Structure):
    _pack_ = 1
    _fields_ = [
        ('PHASE', c_uint8),
        ('MODE', c_uint8),
        ('RSV', c_uint16),
        ('LBA', c_uint32),
        ('KEY', c_uint32),
    ]


class AsyncTrace(Structure):
    _pack_ = 1
    _fields_ = [
        ('entry', DebugInfo*5000),
    ]


class DatasetManagementEntry(Structure):
    _pack_ = 1
    _fields_ = [
        ('DMCA', DatasetManagementContextAttributes),
        ('LENGTH', c_uint32),
        ('SLBA', c_uint64),
    ]


class SglDescriptorFormat(Structure):
    """SGL Descriptor Format"""
    _pack_ = 1
    _fields_ = [
        ('address', c_uint64),
        ('length', c_uint64, 32),
        ('rsv1', c_uint64, 24),
        ('dts', c_uint64, 4),       # Descriptor Type Specific
        ('sdt', c_uint64, 4)        # SGL Descriptor Type
    ]


class LiveMigrationSQE(Structure):
    _pack_ = 1
    _fields_ = [
        ('OPCODE', c_uint32, 8),
        ('FUSE', c_uint32, 2),
        ('RSV0', c_uint32, 4),
        ('PSDT', c_uint32, 2),
        ('CID', c_uint32, 16),
        ('CNTID', c_uint16, 16),
        ('RSV0', c_uint16, 16),
        ('BK_HEAD', c_uint64, 64),
        ('HEAD', c_uint64, 64),
        ('TAIL', c_uint64, 64),
        ('PRP', c_uint64, 64),
        ('CDW10_OPCODE', c_uint32, 8),
        ('CDW10_RSV', c_uint32, 24),
        ('NPAGES', c_uint32, 32),
        ('CDW12', c_uint32, 32),
        ('CDW13', c_uint32, 32),
        ('CDW14', c_uint32, 32),
        ('SUB_OPCODE', c_uint32, 32),
        # ('TIMEOUT', c_uint32),
        # ('RESULT', c_uint32),
    ]


class LVMTrackIOEntry(Structure):
    _pack_ = 1
    _fields_ = [
        ('TYPE', c_uint8, 1),
        ('NSID', c_uint8, 7),
        ('NLB', c_uint16, 16),
        ('SLBA_L', c_uint32),
        ('SLBA_H', c_uint8)

    ]

STATUS_FIELD = {
    0x0: 'Successful Completion',
    0x1: 'Invalid Command Opcode',
    0x2: 'Invalid Field in Command',
    0x3: 'Command ID Conflict',
    0x4: 'Data Transfer Error',
    0x5: 'Commands Aborted due to Power Loss Notification',
    0x6: 'Internal Error',
    0x7: 'Command Abort Requested',
    0x8: 'Command Aborted due to SQ Deletion',
    0x9: 'Command Aborted due to Failed Fused Command',
    0xa: 'Command Aborted due to Missing Fused Command',
    0xb: 'Invalid Namespace or Format',
    0xc: 'Command Sequence Error',
    0xd: 'Invalid SGL Segment Descriptor',
    0xe: 'Invalid Number of SGL Descriptors',
    0xf: 'Data SGL Length Invalid',
    0x10: 'Metadata SGL Length Invalid',
    0x11: 'SGL Descriptor Type Invalid',
    0x12: 'Invalid Use of Controller Memory Buffer',
    0x13: 'PRP Offset Invalid',
    0x14: 'Atomic Write Unit Exceeded',
    0x15: 'Operation Denied',
    0x16: 'SGL Offset Invalid',
    0x18: 'Host Identifier Inconsistent Format',
    0x19: 'Keep Alive Timeout Expired',
    0x1a: 'Keep Alive Timeout Invalid',
    0x1b: 'Command Aborted due to Preempt and Abort',
    0x1c: 'Sanitize Failed',
    0x1d: 'Sanitize In Progress',
    0x1e: 'SGL Data Block Granularity Invalid',
    0x1f: 'Command Not Supported for Queue in CMB',
    0x80: 'LBA Out of Range',
    0x81: 'Capacity Exceeded',
    0x82: 'Namespace Not Ready',
    0x83: 'Reservation Conflict',
    0x84: 'Format In Progress',

    0x100: 'Completion Queue Invalid',
    0x101: 'Invalid Queue Identifier',
    0x102: 'Invalid Queue Size',
    0x103: 'Abort Command Limit Exceeded',
    0x105: 'Asynchronous Event Request Limit Exceeded',
    0x106: 'Invalid Firmware Slot',
    0x107: 'Invalid Firmware Image',
    0x108: 'Invalid Interrupt Vector',
    0x109: 'Invalid Log Page',
    0x10a: 'Invalid Format',
    0x10b: 'Firmware Activation Requires Conventional Reset',
    0x10c: 'Invalid Queue Deletion',
    0x10d: 'Feature Identifier Not Saveable',
    0x10e: 'Feature Not Changeable',
    0x10f: 'Feature Not Namespace Specific',
    0x110: 'Firmware Activation Requires NVM Subsystem Reset',
    0x111: 'Firmware Activation Requires Controller Level Reset',
    0x112: 'Firmware Activation Requires Maximum Time Violation',
    0x113: 'Firmware Activation Prohibited',
    0x114: 'Overlapping Range',
    0x115: 'Namespace Insufficient Capacity',
    0x116: 'Namespace Identifier Unavailable',
    0x118: 'Namespace Already Attached',
    0x119: 'Namespace Is Private',
    0x11a: 'Namespace Not Attached',
    0x11b: 'Thin Provisioning Not Supported',
    0x11c: 'Controller List Invalid',
    0x11d: 'Device Self-test In Progress',
    0x11e: 'Boot Partition Write Prohibited',
    0x11f: 'Invalid Controller Identifier',
    0x120: 'Invalid Secondary Controller State',
    0x121: 'Invalid Number of Controller Resources',
    0x122: 'Invalid Resource Identifier',
    0x180: 'Conflicting Attributes',
    0x181: 'Invalid Protection Information',
    0x182: 'Attempted Write to Read Only Range',

    0x280: 'Write Fault',
    0x281: 'Unrecovered Read Error',
    0x282: 'End-to-end Guard Check Error',
    0x283: 'End-to-end Application Tag Check Error',
    0x284: 'End-to-end Reference Tag Check Error',
    0x285: 'Compare Failure',
    0x286: 'Access Denied',
    0x287: 'Deallocated or Unwritten Logical Block',
}
