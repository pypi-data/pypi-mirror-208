#!/usr/bin/env python
"""
Created on Apr 17, 2017

@author: yyang
"""
from ctypes import Structure, c_uint8, c_uint32, c_uint64, Union
from tool.device.nvme.ctype import Uint128


class CDW(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('BYTE', c_uint8 * 4),
        ]

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]


class Arbitration(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('AB', c_uint32, 3),  # Arbitration Burst (AB)
            ('RSV', c_uint32, 5),
            ('LPW', c_uint32, 8),  # Low Priority Weight (LPW)
            ('MPW', c_uint32, 8),  # Medium Priority Weight (MPW)
            ('HPW', c_uint32, 8),  # High Priority Weight (HPW)
        ]
        desc = {
            'AB': 'Arbitration Burst', 'LPW': 'Low Priority Weight',
            'MPW': 'Medium Priority Weight', 'HPW': 'High Priority Weight'
        }

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class PowerManagement(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('PS', c_uint32, 5),  # Power State
            ('WH', c_uint32, 3),  # Workload Hint
            ('RSV', c_uint32, 24),
        ]
        desc = {'PS': 'Power State', 'WH': 'Workload Hint'}

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class LBARangeType(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('NUM', c_uint32, 6),  # Number of LBA Ranges
            ('RSV', c_uint32, 24),
        ]
        desc = {'NUM': 'Number of LBA Ranges'}

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class LBARangeTypeEntry(Structure):
    _pack_ = 1
    _fields_ = [
        ('TYPE', c_uint8),  # Type
        ('ATTR', c_uint8),  # Attributes
        ('RSV0', c_uint8 * 14),
        ('SLBA', c_uint64),  # Starting LBA
        ('NLB', c_uint64),  # Number of Logical Blocks
        ('GUID', Uint128),  # Unique Identifier
        ('RSV1', c_uint8 * 16),
    ]
    desc = {
        'TYPE': 'Type', 'ATTR': 'Attributes', 'SLBA': 'Starting LBA', 'NLB': 'Number of Logical Blocks',
        'GUID': 'Unique Identifier'
    }


class TemperatureThreshold(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('TMPTH', c_uint32, 16),  # Temperature Threshold
            ('TMPSEL', c_uint32, 4),  # Threshold Temperature Select
            ('THSEL', c_uint32, 2),  # Threshold Type Select
            ('RSV', c_uint32, 10),
        ]
        desc = {'TMPTH': 'Temperature Threshold', 'TMPSEL': 'Threshold Temperature Select',
                'THSEL': 'Threshold Type Select'}

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class ErrorRecovery(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('TLER', c_uint32, 16),  # Time Limited Error Recovery:
            ('DULBE', c_uint32, 1),  # Deallocated or Unwritten Logical Block Error Enable
            ('RSV', c_uint32, 15),
        ]
        desc = {
            'TLER': 'Time Limited Error Recovery:', 'DULBE': 'Deallocated or Unwritten Logical Block Error Enable'
        }

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class VolatileWriteCache(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('WCE', c_uint32, 1),  # Volatile Write Cache Enable
            ('RSV', c_uint32, 31),
        ]
        desc = {'WCE': 'Volatile Write Cache Enable'}

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class NumberOfQueues(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('NSQR', c_uint32, 16),  # Number of I/O Submission Queues Requested (NSQR)
            ('NCQR', c_uint32, 16),  # Number of I/O Completion Queues Requested (NCQR)
        ]
        desc = {
            'NSQR': 'Number of I/O Submission Queues Requested',
            'NCQR': 'Number of I/O Completion Queues Requested'
        }

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class NumberOfQueuesEntry(Structure):
    _pack_ = 1
    _fields_ = [
        ('NSQA', c_uint32, 16),  # Number of I/O Submission Queues Allocated (NSQA)
        ('NCQA', c_uint32, 16),  # Number of I/O Completion Queues Allocated (NCQA)
    ]
    desc = {
        'NSQA': 'Number of I/O Submission Queues Allocated',
        'NCQA': 'Number of I/O Completion Queues Allocated'
    }


class InterruptCoalescing(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('THR', c_uint32, 8),  # Aggregation Threshold
            ('TIME', c_uint32, 8),  # Aggregation Time
            ('RSV0', c_uint32, 16),
        ]
        desc = {'THR': 'Aggregation Threshold', 'TIME': 'Aggregation Time'}

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class InterruptVectorConfiguration(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('IV', c_uint32, 16),  # Interrupt Vector (IV)
            ('CD', c_uint32, 1),  # Coalescing Disable (CD)
            ('RSV', c_uint32, 15),
        ]
        desc = {'IV': 'Interrupt Vector', 'CD': 'Coalescing Disable'}

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class WriteAtomicityNormal(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('DN', c_uint32, 1),  # Disable Normal
            ('RSV', c_uint32, 31),
        ]
        desc = {'DN': 'Disable Normal'}

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class AsynchronousEventConfiguration(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('SHCW', c_uint32, 8),  # SMART / Health Critical Warnings (SHCW)
            ('NAN', c_uint32, 1),  # Namespace Attribute Notices (NAN)
            ('FAN', c_uint32, 1),  # Firmware Activation Notices (FAN)
            ('TLN', c_uint32, 1),  # Telemetry Log Notices (TLN)
            ('RSV', c_uint32, 22),
        ]
        desc = {
            'SHCW': 'SMART / Health Critical Warnings', 'NAN': 'Namespace Attribute Notices',
            'FAN': 'Firmware Activation Notices', 'TLN': 'Telemetry Log Notices'
        }

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class AutonomousPowerStateTransition(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('APSTE', c_uint32, 1),  # Autonomous Power State Transition Enable
            ('RSV', c_uint32, 31),
        ]
        desc = {'APSTE': 'Autonomous Power State Transition Enable'}

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class AutonomousPowerStateTransitionEntry(Structure):
    _pack_ = 1
    _fields_ = [
        ('RSV0', c_uint32, 3),
        ('ITPS', c_uint32, 5),  # Idle Transition Power State
        ('ITPT', c_uint32, 24),  # Idle Time Prior to Transition
        ('RSV1', c_uint32, 32),
    ]
    desc = {'ITPS': 'Idle Transition Power State', 'ITPT': 'Idle Time Prior to Transition'}


class HostMemoryBuffer(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('EHM', c_uint32, 1),  # Enable Host Memory (EHM)
            ('MR', c_uint32, 1),  # Memory Return (MR)
            ('RSV', c_uint32, 30),
        ]
        desc = {'EHM': 'Enable Host Memory', 'MR': 'Memory Return'}

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class HostMemoryBufferDescriptorEntry(Structure):
    _pack_ = 1
    _fields_ = [
        ('BADD', c_uint64),  # Buffer Address (BADD)
        ('BSIZE', c_uint32),  # Buffer Size (BSIZE)
        ('RSV', c_uint32),
    ]
    desc = {'BADD': 'Buffer Address', 'BSIZE': 'Buffer Size'}


class HostMemoryBufferDescriptorList(Structure):
    _pack_ = 1
    _fields_ = [
        ('ENTRY', HostMemoryBufferDescriptorEntry * 256),  # Host Memory Buffer Descriptor Entry
    ]
    desc = {'ENTRY': 'Host Memory Buffer Descriptor Entry'}


class HostMemoryBufferDataStructure(Structure):
    _pack_ = 1
    _fields_ = [
        ('HSIZE', c_uint32),  # Host Memory Buffer Size (HSIZE)
        ('HMDLAL', c_uint32),  # Host Memory Descriptor List Address Lower (HMDLAL)
        ('HMDLAU', c_uint32),  # Host Memory Descriptor List Address Upper (HMDLAU)
        ('HMDLEC', c_uint32),  # Host Memory Descriptor List Entry Count (HMDLEC)
        ('RSV', c_uint64 * 510),
    ]
    desc = {
        'HSIZE': 'Host Memory Buffer Size',
        'HMDLAL': 'Host Memory Descriptor List Address Lower',
        'HMDLAU': 'Host Memory Descriptor List Address Upper',
        'HMDLEC': 'Host Memory Descriptor List Entry Count'
    }


class Timestamp(Structure):
    _pack_ = 1
    _fields_ = [
        ('TIMESTAMP', c_uint64, 48),  # Number of milliseconds that have elapsed since midnight, 01-Jan-1970, UTC.
        ('SYNCH', c_uint64, 1),
        ('TO', c_uint64, 3),  # Timestamp Origin (TO)
        ('RSV0', c_uint64, 4),
        ('RSV1', c_uint64, 8),
    ]
    desc = {'TIMESTAMP': 'Number of milliseconds since 01-Jan-1970, UTC', 'TO': 'Timestamp Origin'}


class KeepAliveTimer(Structure):
    _pack_ = 1
    _fields_ = [
        ('KATO', c_uint32),  # Persist Through Power Loss (KATO)
    ]
    desc = {'KATO': 'Persist Through Power Loss'}


class HostControlledThermalManagement(Structure):
    _pack_ = 1
    _fields_ = [
        ('TMT2', c_uint32, 16),  # Thermal Management Temperature (TMT)
        ('TMT1', c_uint32, 16),
    ]
    desc = {'TMT2': 'Thermal Management Temperature 2', 'TMT1': 'Thermal Management Temperature 1'}


class NonOperationalPowerStateConfig(Structure):
    _pack_ = 1
    _fields_ = [
        ('NOPPME', c_uint32, 1),  # Non-Operational Power State Permissive Mode Enable (NOPPME)
        ('RSV', c_uint32, 31),
    ]
    desc = {'NOPPME': 'Non-Operational Power State Permissive Mode Enable'}


class ReadRecoveryLevelConfig(Structure):
    _pack_ = 1
    _fields_ = [
        ('RRL', c_uint32, 4),
        ('RSV0', c_uint32, 28),
    ]


class SanitizeConfig(Structure):
    _pack_ = 1
    _fields_ = [
        ('NODRM', c_uint32, 1),
        ('RSV0', c_uint32, 31),
    ]


class SoftwareProgressMarker(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('PBSLC', c_uint32, 8),
            ('RSV', c_uint32, 24),
        ]
        desc = {'PBSLC': 'Pre-boot Software Load Count'}

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class HostIdentifier(Union):
    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('EXHID', c_uint32, 1), # Enable Extended Host Identifier
            ('RSV', c_uint32, 31),
        ]
        desc = {'EXHID': 'Enable Extended Host Identifier'}

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('DWORD', c_uint32),
        ('BITS', BITS),
    ]
    desc = {'DWORD': 'Command Dword'}


class HostIdentifierEntry(Structure):
    _pack_ = 1
    _fields_ = [
        ('HOSTIDL', c_uint64),
        ('HOSTIDH', c_uint64),  # HOSTID
    ]
    desc = {
        'HOSTIDL': 'Host Identifie',
        'HOSTIDH': 'Host Identifie'
    }


class ReservationNotificationMask(Structure):
    _pack_ = 1
    _fields_ = [
        ('RSV0', c_uint32, 1),
        ('REGPRE', c_uint32, 1),  # Mask Registration Preempted Notification
        ('RESREL', c_uint32, 1),  # Mask Reservation Released Notification
        ('RESPRE', c_uint32, 1),  # Mask Reservation Preempted Notification
        ('RSV1', c_uint32, 28),
    ]
    desc = {
        'REGPRE': 'Mask Registration Preempted Notification', 'RESREL': 'Mask Reservation Released Notification',
        'RESPRE': 'Mask Reservation Preempted Notification'
    }


class ReservationPersistence(Structure):
    _pack_ = 1
    _fields_ = [
        ('PTPL', c_uint32, 1),  # Persist Through Power Loss (PTPL)
        ('RSV0', c_uint32, 31),
    ]
    desc = {'PTPL': 'Persist Through Power Loss'}


class FeatureID(object):
    Arbitration = 0x1
    PowerManagement = 0x2
    LBARangeType = 0x3
    TemperatureThreshold = 0x4
    ErrorRecovery = 0x5
    VolatileWriteCache = 0x6
    NumberOfQueues = 0x7
    InterruptCoalescing = 0x8
    InterruptVectorConfiguration = 0x9
    WriteAtomicityNormal = 0xa
    AsynchronousEventConfiguration = 0xb
    AutonomousPowerStateTransition = 0xc
    HostMemoryBuffer = 0xd
    Timestamp = 0xe
    KeepAliveTimer = 0xf
    HostControlledThermalManagement = 0x10
    NonOperationalPowerStateConfig = 0x11
    ReadRecoveryLevelConfig = 0x12
    PredictableLatencyModeConfig = 0x13
    PredictableLatencyModeWindow = 0x14
    LBAStatusInfoReportInterval = 0x15
    HostBehaviorSupport = 0x16
    SanitizeConfig = 0x17
    EnduranceGroupEventConfig = 0x18
    SoftwareProgressMarker = 0x80
    HostIdentifier = 0x81
    ReservationNotificationMask = 0x82
    ReservationPersistence = 0x83
    NamespaceWriteProtectionConfig = 0x84


GET_FEATURE_ID = {
    0x1: Arbitration,
    0x2: PowerManagement,
    0x3: LBARangeType,
    0x4: TemperatureThreshold,
    0x5: ErrorRecovery,
    0x6: VolatileWriteCache,
    0x7: NumberOfQueues,
    0x8: InterruptCoalescing,
    0x9: InterruptVectorConfiguration,
    0xa: WriteAtomicityNormal,
    0xb: AsynchronousEventConfiguration,
    0xc: AutonomousPowerStateTransition,
    0xd: HostMemoryBuffer,
    0xf: KeepAliveTimer,
    0x10: HostControlledThermalManagement,
    0x11: NonOperationalPowerStateConfig,
    0x80: SoftwareProgressMarker,
    0x81: HostIdentifier,
    0x82: ReservationNotificationMask,
    0x83: ReservationPersistence,
}

GET_FEATURE_ENTRY = {
    0x3: LBARangeTypeEntry,
    0xd: HostMemoryBufferDataStructure,
    0xe: Timestamp,
}
