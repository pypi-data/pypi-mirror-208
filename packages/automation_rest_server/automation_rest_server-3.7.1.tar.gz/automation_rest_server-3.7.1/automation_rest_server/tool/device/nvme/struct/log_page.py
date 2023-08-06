#!/usr/bin/env python
# pylint: disable=superfluous-parens,missing-docstring,too-few-public-methods
"""
Created on Apr 19, 2019

@author: yyang
"""
from ctypes import Structure, c_uint8, c_uint16, c_uint32, c_uint64, Union
from tool.device.nvme.ctype import Uint128, Byte


class ErrorInformation(Structure):
    """Get Log Page - Error Information (Log Identifier 01h)"""
    _pack_ = 1
    _fields_ = [
        ('COUNT', c_uint64),  # Error Count
        ('SQID', c_uint16),  # Submission Queue ID
        ('CID', c_uint16),  # Command ID
        ('STATUS', c_uint16),  # Status Field
        ('PEL', c_uint16),  # Parameter Error Location
        ('LBA', c_uint64),  # LBA
        ('NSID', c_uint32),  # Namespace
        ('VSIA', c_uint8),  # Vendor Specific Information Available
        ('RSV0', c_uint8 * 3),
        ('CSI', c_uint64),  # Command Specific Information
        ('RSV1', c_uint8 * 24),
    ]
    desc = {
        'COUNT': 'Error Count', 'SQID': 'Submission Queue ID', 'CID': 'Command ID', 'STATUS': 'Status Field',
        'PEL': 'Parameter Error Location', 'LBA': 'LBA', 'NSID': 'Namespace',
        'VSIA': 'Vendor Specific Information Available', 'CSI': 'Command Specific Information'
    }


class SmartHealthInformation(Structure):
    """Get Log Page - SMART/Health Information (Log Identifier 02h)"""
    _pack_ = 1
    _fields_ = [
        ('CW', c_uint8),  # Critical Warning
        ('CT', c_uint16),  # Composite Temperature
        ('AS', c_uint8),  # Available Spare
        ('AST', c_uint8),  # Available Spare Threshold
        ('PU', c_uint8),  # Percentage Used
        ('EGCWS', c_uint8),  # Endurance Group Critical Warning Summary
        ('RSV0', c_uint8 * 25),
        ('DUR', Uint128),  # Data Units Read
        ('DUW', Uint128),  # Data Units Write
        ('HRC', Uint128),  # Host Read Commands
        ('HWC', Uint128),  # Host Write Commands
        ('CBT', Uint128),  # Controller Busy Time
        ('PC', Uint128),  # Power Cycles
        ('POH', Uint128),  # Power On Hours
        ('US', Uint128),  # Unsafe Shutdowns
        ('MDIE', Uint128),  # Media and Data Integrity Errors
        ('NEILE', Uint128),  # Number of Error Information Log Entries
        ('WCTT', c_uint32),  # Warning Composite Temperature Time
        ('CCTT', c_uint32),  # Critical Composite Temperature Time
        ('TS', c_uint16 * 8),  # Temperature Sensor 1 ~ 8
        ('TMT1TC', c_uint32),  # Thermal Management Temperature 1 Transition Count
        ('TMT2TC', c_uint32),  # Thermal Management Temperature 2 Transition Count
        ('TTFTMT1', c_uint32),  # Total Time For Thermal Management Temperature 1
        ('TTFTMT2', c_uint32),  # Total Time For Thermal Management Temperature 2
        ('RSV1', c_uint8 * 280),
    ]
    desc = {
        'CW': 'Critical Warning', 'CT': 'Composite Temperature', 'AS': 'Available Spare',
        'AST': 'Available Spare Threshold', 'PU': 'Percentage Used',
        'EGCWS': 'Endurance Group Critical Warning Summary', 'DUR': 'Data Units Read',
        'DUW': 'Data Units Write', 'HRC': 'Host Read Commands', 'HWC': 'Host Write Commands',
        'CBT': 'Controller Busy Time', 'PC': 'Power Cycles', 'POH': 'Power On Hours',
        'US': 'Unsafe Shutdowns', 'MDIE': 'Media and Data Integrity Errors',
        'NEILE': 'Number of Error Information Log Entries', 'WCTT': 'Warning Composite Temperature Time',
        'CCTT': 'Critical Composite Temperature Time', 'TS': 'Temperature Sensor',
        'TMT1TC': 'Thermal Management Temperature 1 Transition Count',
        'TMT2TC': 'Thermal Management Temperature 2 Transition Count',
        'TTFTMT1': 'Total Time For Thermal Management Temperature 1',
        'TTFTMT2': 'Total Time For Thermal Management Temperature 2',
    }


class FirmwareSlotInformation(Structure):
    """Get Log Page - Firmware Slot Information (Log Identifier 03h)"""
    _pack_ = 1
    _fields_ = [
        ('AFI', c_uint8),  # Active Firmware Info (AFI)
        ('RSV0', c_uint8 * 7),
        ('FRS1', Byte * 8),  # Firmware Revision for Slot 1 (FRS1)
        ('FRS2', Byte * 8),  # Firmware Revision for Slot 2 (FRS2)
        ('FRS3', Byte * 8),  # Firmware Revision for Slot 3 (FRS3)
        ('FRS4', Byte * 8),  # Firmware Revision for Slot 4 (FRS4)
        ('FRS5', Byte * 8),  # Firmware Revision for Slot 5 (FRS5)
        ('FRS6', Byte * 8),  # Firmware Revision for Slot 6 (FRS6)
        ('FRS7', Byte * 8),  # Firmware Revision for Slot 7 (FRS7)
        ('RSV1', c_uint8 * 4032)
    ]
    desc = {
        'AFI': 'Active Firmware Info', 'FRS1': 'Firmware Revision for Slot 1',
        'FRS2': 'Firmware Revision for Slot 2', 'FRS3': 'Firmware Revision for Slot 3',
        'FRS4': 'Firmware Revision for Slot 4', 'FRS5': 'Firmware Revision for Slot 5',
        'FRS6': 'Firmware Revision for Slot 6', 'FRS7': 'Firmware Revision for Slot 7',
    }


class ChangedNamespaceList(Structure):
    """Get Log Page - Changed Namespace list data structure"""
    _pack_ = 1
    _fields_ = [
        ('ID', c_uint64 * 1024)
    ]
    desc = {
        'ID': 'Identifier Index',
    }


class CommandEffectDataStructure(Structure):
    """Get Log Page - Command Effect Data Structure (Log Identifier 05h)"""
    _pack_ = 1
    _fields_ = [
        ('csupp', c_uint32, 1),
        ('lbcc', c_uint32, 1),
        ('ncc', c_uint32, 1),
        ('nic', c_uint32, 1),
        ('ccc', c_uint32, 1),
        ('rsv0', c_uint32, 11),
        ('cse', c_uint32, 3),
        ('rsv1', c_uint32, 13),
    ]


class CommandsSupportAndEffects(Structure):
    _pack_ = 1
    _fields_ = [
        ('ACS', CommandEffectDataStructure * 256),
        ('IOCS', CommandEffectDataStructure * 256),
        ('RSV', c_uint8 * 2048),
    ]
    desc = {
        'ACS': 'Admin Command Supported', 'IOCS': 'I/O Command Supported',
    }


class SelfTestResult(Structure):
    """Get Log Page - Device Self-test data structure"""
    _pack_ = 1
    _fields_ = [
        ('DSTS', c_uint8),
        ('SN', c_uint8),
        ('VDI', c_uint8),
        ('RSV', c_uint8),
        ('POH', c_uint64),
        ('NSID', c_uint32),
        ('FLBA', c_uint64),
        ('SCT', c_uint8),
        ('SC', c_uint8),
        ('VS', c_uint16)
    ]
    desc = {
        'DSTS': 'device selt-test status', 'SN': 'segment number', 'VDI': 'valid diagnostic information',
        'POH': 'power on hours', 'NSID': 'namespace identifier', 'FLBA': 'failing lba',
        'SCT': 'status code type', 'SC': 'status code', 'VS': 'vendor specific',
    }


class SelfTestLog(Structure):
    """Get Log Page - Device Self-test (Log Identifier 06h)"""
    _pack_ = 1
    _fields_ = [
        ('CDSTO', c_uint8),  # current device self-test operation
        ('CDSTC', c_uint8),  # current device self-test completion
        ('RSV', c_uint16),
        ('RESULT', SelfTestResult * 20)  # self test result data structure
    ]
    desc = {
        'CDSTO': 'current device self-test operation', 'CDSTC': 'current device self-test completion',
        'RESULT': 'self test result data structure',
    }


class TelemetryDataBlock(Structure):
    """Get Log Page - Telemetry Data Block Structure"""
    _pack_ = 1
    _fields_ = [
        ('DATA', c_uint8 * 512),  # Telemetry Data Block
    ]
    desc = {
        'DATA': 'Telemetry Data Block',
    }


class TelemetryHostInitiated(Structure):
    """Get Log Page - Telemetry Host-Initiated Log(Log Identifier 07h)"""
    _pack_ = 1
    _fields_ = [
        ('LID', c_uint8),  # Log Identifier, This field shall be set to 07h.
        ('RSV0', c_uint32),  # Reserved 0
        ('IEEE', c_uint8 * 3),  # IEEE OUI Identifier
        ('THIDA1LB', c_uint16),  # Telemetry Host-Initiated Data Area 1 Last Block
        ('THIDA2LB', c_uint16),  # Telemetry Host-Initiated Data Area 2 Last Block
        ('THIDA3LB', c_uint16),  # Telemetry Host-Initiated Data Area 3 Last Block
        ('RSV1', c_uint8 * 368),  # Reserved 1
        ('TCIDA', c_uint8),  # Telemetry Controller-Initiated Data Available
        ('TCIDGN', c_uint8),  # Telemetry Controller-Initiated Data Generation Number
        ('RID', c_uint8 * 128),  # Reason Identifier
        ('THIDB', TelemetryDataBlock * 7),  # Telemetry Host-Initiated Data Block 1 - n
    ]
    desc = {
        'LID': 'Log Identifier', 'IEEE': 'IEEE OUI Identifier',
        'THIDA1LB': 'Telemetry Host-Initiated Data Area 1 Last Block',
        'THIDA2LB': 'Telemetry Host-Initiated Data Area 2 Last Block',
        'THIDA3LB': 'Telemetry Host-Initiated Data Area 3 Last Block',
        'TCIDA': 'Telemetry Controller-Initiated Data Available',
        'TCIDGN': 'Telemetry Controller-Initiated Data Generation Number',
        'RID': 'Reason Identifier', 'THIDB': 'Telemetry Host-Initiated Data Block',
    }


class TelemetryControllerInitiated(Structure):
    """Get Log Page - Telemetry Controller-Initiated Log(Log Identifier 08h)"""
    _pack_ = 1
    _fields_ = [
        ('LID', c_uint8),  # Log Identifier, This field shall be set to 08h.
        ('RSV0', c_uint32),  # Reserved 0
        ('IEEE', c_uint8 * 3),  # IEEE OUI Identifier
        ('TCIDA1LB', c_uint16),  # Telemetry Controller-Initiated Data Area 1 Last Block
        ('TCIDA2LB', c_uint16),  # Telemetry Controller-Initiated Data Area 2 Last Block
        ('TCIDA3LB', c_uint16),  # Telemetry Controller-Initiated Data Area 3 Last Block
        ('RSV1', c_uint8 * 368),  # Reserved 1
        ('TCIDA', c_uint8),  # Telemetry Controller-Initiated Data Available
        ('TCIDGN', c_uint8),  # Telemetry Controller-Initiated Data Generation Number
        ('RID', c_uint8 * 128),  # Reason Identifier
        ('TCIDB', TelemetryDataBlock * 7),  # Telemetry Host-Initiated Data Block 1 - n
    ]
    desc = {
        'LID': 'Log Identifier', 'IEEE': 'IEEE OUI Identifier',
        'TCIDA1LB': 'Telemetry Controller-Initiated Data Area 1 Last Block',
        'TCIDA2LB': 'Telemetry Controller-Initiated Data Area 2 Last Block',
        'TCIDA3LB': 'Telemetry Controller-Initiated Data Area 3 Last Block',
        'TCIDA': 'Telemetry Controller-Initiated Data Available',
        'TCIDGN': 'Telemetry Controller-Initiated Data Generation Number',
        'RID': 'Reason Identifier', 'TCIDB': 'Telemetry Controller-Initiated Data Block',
    }


class ReservationNotificationLog(Structure):
    """Get Log Page - Reservation Notification (Log Identifier 80h)"""
    _pack_ = 1
    _fields_ = [
        ('LPC', c_uint64),
        ('RNLPT', c_uint8),
        ('NALP', c_uint8),
        ('RSV0', c_uint8 * 2),
        ('NSID', c_uint32),
        ('RSV1', c_uint8 * 48),
    ]
    desc = {
        'LPC': 'Log Page Count', 'RNLPT': 'Reservation Notification Log Page Type',
        'NALP': 'Number of Available Log Pages', 'NSID': 'Namespace ID:',
    }


class SanitizeStatusLog(Structure):
    """Get Log Page - Reservation Notification (Log Identifier 81h)"""
    _pack_ = 1
    _fields_ = [
        ('SPROG', c_uint16),
        ('SSTAT', c_uint16),
        ('SCDW10', c_uint32),
        ('ETFO', c_uint32),
        ('ETFBE', c_uint32),
        ('ETFCE', c_uint32),
        ('ETFOWND', c_uint32),
        ('ETFBEWND', c_uint32),
        ('ETFCEWND', c_uint32),
        ('RAV0', c_uint8 * 480),
    ]
    desc = {
        'SPROG': 'Sanitize Progress', 'SSTAT': 'Sanitize Status',
        'SCDW10': 'Sanitize Command Dword 10 Information', 'ETFO': 'Estimated Time For Overwrite',
        'ETFBE': 'Estimated Time For Block Erase', 'ETFCE': 'Estimated Time For Crypto Erase:',
        'ETFOWND': 'Estimated Time For Overwrite With No-Deallocate Media Modification',
        'ETFBEWND': 'Estimated Time For Block Erase With No-Deallocate Media Modification',
        'ETFCEWND': 'Estimated Time For Crypto Erase With No-Deallocate Media Modification',
    }

class BadBlockHeader(Structure):
    """Get Log Page - CNEX Bad Block (Log Identifier CBh)"""
    _pack_ = 1
    _fields_ = [
        ('SN', Byte * 20),  # Serial Number
        ('RN', c_uint32),  # Revision Number
        ('NE', c_uint32),  # NAND Entities
        ('NOF', c_uint32),  # Number Of FBB
        ('NOM', c_uint32),  # Number Of MBB
        ('NOG', c_uint32),  # Number Of GBB
        ('FBS', c_uint32),  # FBB Bitmap Start
        ('MBS', c_uint32),  # MBB Bitmap Start
        ('GBS', c_uint32),  # GBB Bitmap Start
        ('BDS', c_uint32),  # BB Details Start
        ('TL', c_uint32),  # Total Length
        ('UUID', Uint128 * 128),  # UUIDs
        ('RSV', c_uint8 * 1988),
    ]
    desc = {
        'SN': 'Serial Number', 'RN': 'Revision Number', 'NE': 'NAND Entities', 'NOF': 'Number Of FBB',
        'NOM': 'Number Of MBB', 'NOG': 'Number Of GBB', 'FBS': 'FBB Bitmap Start', 'MBS': 'MBB Bitmap Start',
        'GBS': 'GBB Bitmap Start', 'BDS': 'BB Details Start', 'TL': 'Total Length',
    }


class BadBlockDetails(Union):
    """Get Log Page - CNEX Bad Block (Log Identifier CBh)"""

    class BITS(Structure):
        _pack_ = 1
        _fields_ = [
            ('TYPE', c_uint64, 3),  # 0: Erase Error, 1: Write Error, 2: Read Error
            ('POT', c_uint64, 13),  # Power On Time
            ('PC', c_uint64, 16),  # PE Cycle
            ('BL', c_uint64, 13),
            ('PL', c_uint64, 3),
            ('LN', c_uint64, 4),
            ('CH', c_uint64, 4),
            ('RSV', c_uint64, 8),
        ]
        desc = {
            'POT': 'Power On Time', 'PC': 'PE Cycle', 'BL': 'Block', 'PL': 'Plane',
            'LN': 'Lun', 'CH': 'Channel'
        }

    _anonymous_ = ('BITS',)
    _fields_ = [
        ('QWORD', c_uint64),
        ('DWORD', c_uint32 * 2),
        ('BITS', BITS),
    ]
