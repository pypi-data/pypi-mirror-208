#!/usr/bin/env python
# pylint: disable=superfluous-parens,missing-docstring,too-few-public-methods
"""
Created on Apr 19, 2019

@author: yyang
"""
from ctypes import Structure, c_uint8, c_uint16, c_uint32, c_uint64
from tool.device.nvme.ctype import Uint128, Byte


class PowerStateDescriptorDataStructure(Structure):
    """Identify - Power State Descriptor Data Structure"""
    _pack_ = 1
    _fields_ = [
        ('MP', c_uint16),  # Maximum Power (MP)
        ('RSV0', c_uint8),
        ('MXPS', c_uint8, 1),  # Max Power Scale (MXPS)
        ('NOPS', c_uint8, 1),  # Non-Operational State (NOPS)
        ('RSV1', c_uint8, 6),
        ('ENLAT', c_uint32),  # Entry Latency (ENLAT)
        ('EXLAT', c_uint32),  # Exit Latency (EXLAT)
        ('RRT', c_uint8, 5),  # Relative Read Throughput (RRT)
        ('RSV2', c_uint8, 3),
        ('RRL', c_uint8, 5),  # Relative Read Latency (RRL)
        ('RSV3', c_uint8, 3),
        ('RWT', c_uint8, 5),  # Relative Write Throughput (RWT)
        ('RSV4', c_uint8, 3),
        ('RWL', c_uint8, 5),  # Relative Write Latency (RWL)
        ('RSV5', c_uint8, 3),
        ('IDLP', c_uint16),  # Idle Power (IDLP)
        ('RSV6', c_uint8, 6),
        ('IPS', c_uint8, 2),  # Idle Power Scale (IPS)
        ('RSV7', c_uint8),
        ('ACTP', c_uint16),  # Active Power (ACTP)
        ('APW', c_uint8, 3),  # Active Power Workload (APW)
        ('RSV8', c_uint8, 3),
        ('APS', c_uint8, 2),  # Active Power Scale (APS)
        ('RSV9', c_uint8 * 9),
    ]
    desc = {
        'MP': 'Maximum Power', 'MXPS': 'Max Power Scale', 'NOPS': 'Non-Operational State',
        'ENLAT': 'Entry Latency', 'EXLAT': 'Exit Latency', 'RRT': 'Relative Read Throughput',
        'RRL': 'Relative Read Latency', 'RWT': 'Relative Write Throughput', 'RWL': 'Relative Write Latency',
        'IDLP': 'Idle Power', 'IPS': 'Idle Power Scale', 'ACTP': 'Active Power', 'APW': 'Active Power Workload',
        'APS': 'Active Power Scale'
    }


class ControllerDataStructure(Structure):
    """Identify - Identify Controller Data Structure"""
    _pack_ = 1
    _fields_ = [
        ('VID', c_uint16),  # PCI Vendor ID
        ('SSVID', c_uint16),  # PCI Subsystem Vendor ID
        ('SN', Byte * 20),  # Serial number
        ('MN', Byte * 40),  # Model number for the NVM subsystem
        ('FR', Byte * 8),  # Firmware revision for the NVM subsystem
        ('RAB', c_uint8),  # Recommended Arbitration Burst size
        ('IEEE', c_uint32, 24),  # IEEE OUI Identifier
        ('CMIC', c_uint32, 8),  # Controller Multi-Path I/O and Namespace Sharing Capabilities
        ('MDTS', c_uint8),  # Maximum Data Transfer Size
        ('CNTLID', c_uint16),  # Controller ID
        ('VER', c_uint32),  # Version
        ('RTD3R', c_uint32),  # RTD3 Resume Latency
        ('RTD3E', c_uint32),  # RTD3 Entry Latency
        ('OAES', c_uint32),  # Optional Asynchronous Events Supported
        ('CTRATT', c_uint32),  # Controller Attributes (CTRATT)
        ('RSV0', c_uint8 * 12),
        ('FGUID', Byte * 12),  # FRU Globally Unique Identifier (FGUID)
        ('RSV1', c_uint8 * 116),
        ('MMIS', Byte * 16),  # NVMe Management Interface Specification
        ('OACS', c_uint16),  # Optional Admin Command Support
        ('ACL', c_uint8),  # Abort Command Limit
        ('AERL', c_uint8),  # Asynchronous Event Request Limit
        ('FRMW', c_uint8),  # Firmware Updates
        ('LPA', c_uint8),  # Log Page Attributes
        ('ELPE', c_uint8),  # Error Log Page Entries
        ('NPSS', c_uint8),  # Number of Power States Support
        ('AVSCC', c_uint8),  # Admin Vendor Specific Command Configuration
        ('APSTA', c_uint8),  # Autonomous Power State Transition Attributes
        ('WCTEMP', c_uint16),  # Warning Composite Temperature Threshold
        ('CCTEMP', c_uint16),  # Critical Composite Temperature Threshold
        ('MTFA', c_uint16),  # Maximum Time for Firmware Activation
        ('HMPRE', c_uint32),  # Host Memory Buffer Preferred Size
        ('HMMIN', c_uint32),  # Host Memory Buffer Minimum Size
        ('TNVMCAP', Uint128),  # Total NVM Capacity
        ('UNVMCAP', Uint128),  # Unallocated NVM Capacity
        ('RPMBS', c_uint32),  # Replay Protected Memory Block Support
        ('EDSTT', c_uint16),  # Extended Device Self-test Time (EDSTT)
        ('DSTO', c_uint8),  # Device Self-test Options (DSTO)
        ('FWUG', c_uint8),  # Firmware Update Granularity (FWUG)
        ('KAS', c_uint16),  # Keep Alive Support (KAS)
        ('HCTMA', c_uint16),  # Host Controlled Thermal Management Attributes (HCTMA)
        ('MNTMT', c_uint16),  # Minimum Thermal Management Temperature (MNTMT)
        ('MXTMT', c_uint16),  # Maximum Thermal Management Temperature (MXTMT)
        ('SANICAP', c_uint32),  # Sanitize Capabilities (SANICAP)
        ('RSV2', c_uint8 * 180),
        ('SQES', c_uint8),  # Submission Queue Entry Size
        ('CQES', c_uint8),  # Completion Queue Entry Size
        ('MAXCMD', c_uint16),  # Maximum Outstanding Commands (MAXCMD)
        ('NN', c_uint32),  # Number of Namespaces
        ('ONCS', c_uint16),  # Optional NVM Command Support
        ('FUSES', c_uint16),  # Fused Operation Support
        ('FNA', c_uint8),  # Format NVM Attributes
        ('VWC', c_uint8),  # Volatile Write Cache
        ('AWUN', c_uint16),  # Atomic Write Unit Normal
        ('AWUPF', c_uint16),  # Atomic Write Unit Power Fail
        ('NVSCC', c_uint8),  # NVM Vendor Specific Command Configuration
        ('RSV3', c_uint8),
        ('ACWU', c_uint16),  # Atomic Compare & Write Unit
        ('RSV4', c_uint8 * 2),
        ('SGLS', c_uint32),  # SGL Support
        ('RSV5', c_uint8 * 28),
        ('SUBNQN', Byte * 256),  # NVM Subsystem NVMe Qualified Name
        ('RSV6', c_uint8 * 768),
        ('PSD', PowerStateDescriptorDataStructure * 32),  # Power State Descriptor
        ('VS', Byte * 1024),  # Vendor Specific
    ]
    desc = {
        'VID': 'PCI Vendor ID', 'SSVID': 'PCI Subsystem Vendor ID', 'SN': 'Serial number',
        'MN': 'Model number for the NVM subsystem', 'FR': 'Firmware revision for the NVM subsystem',
        'RAB': 'Recommended Arbitration Burst size', 'IEEE': 'IEEE OUI Identifier',
        'CMIC': 'Controller Multi-Path I/O and Namespace Sharing Capabilities', 'MDTS': 'Maximum Data Transfer Size',
        'CNTLID': 'Controller ID', 'VER': 'Version', 'RTD3R': 'RTD3 Resume Latency', 'RTD3E': 'RTD3 Entry Latency',
        'OAES': 'Optional Asynchronous Events Supported', 'CTRATT': 'Controller Attributes',
        'FGUID': 'FRU Globally Unique Identifier', 'MMIS': 'NVMe Management Interface Specification',
        'OACS': 'Optional Admin Command Support', 'ACL': 'Abort Command Limit',
        'AERL': 'Asynchronous Event Request Limit', 'FRMW': 'Firmware Updates', 'LPA': 'Log Page Attributes',
        'ELPE': 'Error Log Page Entries', 'NPSS': 'Number of Power States Support',
        'AVSCC': 'Admin Vendor Specific Command Configuration', 'APSTA': 'Autonomous Power State Transition Attributes',
        'WCTEMP': 'Warning Composite Temperature Threshold', 'CCTEMP': 'Critical Composite Temperature Threshold',
        'MTFA': 'Maximum Time for Firmware Activation', 'HMPRE': 'Host Memory Buffer Preferred Size',
        'HMMIN': 'Host Memory Buffer Minimum Size', 'TNVMCAP': 'Total NVM Capacity',
        'UNVMCAP': 'Unallocated NVM Capacity', 'RPMBS': 'Replay Protected Memory Block Support',
        'EDSTT': 'Extended Device Self-test Time', 'DSTO': 'Device Self-test Options',
        'FWUG': 'Firmware Update Granularity', 'KAS': 'Keep Alive Support',
        'HCTMA': 'Host Controlled Thermal Management Attributes', 'MNTMT': 'Minimum Thermal Management Temperature',
        'MXTMT': 'Maximum Thermal Management Temperature', 'SANICAP': 'Sanitize Capabilities',
        'SQES': 'Submission Queue Entry Size', 'CQES': 'Completion Queue Entry Size',
        'MAXCMD': 'Maximum Outstanding Commands', 'NN': 'Number of Namespaces',
        'ONCS': 'Optional NVM Command Support', 'FUSES': 'Fused Operation Support',
        'FNA': 'Format NVM Attributes', 'VWC': 'Volatile Write Cache', 'AWUN': 'Atomic Write Unit Normal',
        'AWUPF': 'Atomic Write Unit Power Fail', 'NVSCC': 'NVM Vendor Specific Command Configuration',
        'ACWU': 'Atomic Compare & Write Unit', 'SGLS': 'SGL Support', 'SUBNQN': 'NVM Subsystem NVMe Qualified Name',
        'PSD': 'Power State Descriptor',
        'VS': 'Vendor Specific'
    }


class LBAFormatDataStructure(Structure):
    """Identify - LBA Format Data Structure, NVM Command Set Specific"""
    _pack_ = 1
    _fields_ = [
        ('MS', c_uint32, 16),  # Metadata Size
        ('LBADS', c_uint32, 8),  # LBA Data Size
        ('RP', c_uint32, 2),  # Relative Performance
        ('RSV', c_uint32, 6),
    ]
    desc = {
        'MS': 'Metadata Size', 'LBADS': 'LBA Data Size', 'RP': 'Relative Performance'
    }


class NamespaceDataStructure(Structure):
    """Identify - Identify Namespace Data Structure, NVM Command Set Specific"""
    _pack_ = 1
    _fields_ = [
        ('NSIZE', c_uint64),  # Namespace Size
        ('NCAP', c_uint64),  # Namespace Capacity
        ('NUSE', c_uint64),  # Namespace Utilization
        ('NSFEAT', c_uint8),  # Namespace Features
        ('NLBAF', c_uint8),  # Number of LBA Formats
        ('FLBAS', c_uint8),  # Formatted LBA Size
        ('MC', c_uint8),  # Metadata Capabilities
        ('DPC', c_uint8),  # End-to-end Data Protection Capabilities
        ('DPS', c_uint8),  # End-to-end Data Protection Type Settings
        ('NMIC', c_uint8),  # Namespace Multi-path I/O and Namespace Sharing Capabilities
        ('RESCAP', c_uint8),  # Reservation Capabilities
        ('FPI', c_uint8),  # Format Progress Indicator
        ('DLFEAT', c_uint8),  # Deallocate Logical Block Features (DLFEAT)
        ('NAWUN', c_uint16),  # Namespace Atomic Write Unit Normal (NAWUN)
        ('NAWUPF', c_uint16),  # Namespace Atomic Write Unit Power Fail (NAWUPF)
        ('NACWU', c_uint16),  # Namespace Atomic Compare & Write Unit
        ('NABSN', c_uint16),  # Namespace Atomic Boundary Size Normal
        ('NABO', c_uint16),  # Namespace Atomic Boundary Offset
        ('NABSPF', c_uint16),  # Namespace Atomic Boundary Size Power Fail
        ('NOIOB', c_uint16),  # Namespace Optimal IO Boundary (NOIOB)
        ('NVMCAP', Uint128),  # NVM Capacity (NVMCAP)
        ('RSV0', c_uint8 * 40),
        ('NGUID', Byte * 16),  # Namespace Globally Unique Identifier
        ('EUI64', c_uint64),  # IEEE Extended Unique Identifier
        ('LBAF', LBAFormatDataStructure * 16),  # LBA Format Support
        ('RSV1', c_uint8 * 192),
        ('VS', Byte * 3712),  # Vendor Specific
    ]
    desc = {
        'NSIZE': 'Namespace Size', 'NCAP': 'Namespace Capacity', 'NUSE': 'Namespace Utilization',
        'NSFEAT': 'Namespace Features', 'NLBAF': 'Number of LBA Formats', 'FLBAS': 'Formatted LBA Size',
        'MC': 'Metadata Capabilities', 'DPC': 'End-to-end Data Protection Capabilities',
        'DPS': 'End-to-end Data Protection Type Settings',
        'NMIC': 'Namespace Multi-path I/O and Namespace Sharing Capabilities',
        'RESCAP': 'Reservation Capabilities', 'FPI': 'Format Progress Indicator',
        'DLFEAT': 'Deallocate Logical Block Features', 'NAWUN': 'Namespace Atomic Write Unit Normal',
        'NAWUPF': 'Namespace Atomic Write Unit Power Fail', 'NACWU': 'Namespace Atomic Compare & Write Unit',
        'NABSN': 'Namespace Atomic Boundary Size Normal', 'NABO': 'Namespace Atomic Boundary Offset',
        'NABSPF': 'Namespace Atomic Boundary Size Power Fail', 'NOIOB': 'Namespace Optimal IO Boundary',
        'NVMCAP': 'NVM Capacity', 'NGUID': 'Namespace Globally Unique Identifier',
        'EUI64': 'IEEE Extended Unique Identifier', 'LBAF': 'LBA Format Support', 'VS': 'Vendor Specific'
    }


class PrimaryControllerCap(Structure):
    """Identify - PrimaryController Data Structure"""
    _pack_ = 1
    _fields_ = [
        ('CNTLID', c_uint16),  # Controller Identifier
        ('PORTID', c_uint16),  # Port Identifier
        ('CRT', c_uint8),  # Controller Resource Types
        ('RSV0', c_uint8 * 27),
        ('VQFRT', c_uint32),  # VQ Resources Flexible Total
        ('VQRFA', c_uint32),  # VQ Resources Flexible Assigned
        ('VQRFAP', c_uint16),  # VQ Resources Flexible Allocated to Primary
        ('VQPRT', c_uint16),  # VQ Resources Private Total
        ('VQFRSM', c_uint16),  # VQ Resources Flexible Secondary Maximum
        ('VQGRAN', c_uint16),  # VQ Flexible Resource Preferred Granularity
        ('RSV1', c_uint8 * 16),
        ('VIFRT', c_uint32),  # VI Resources Flexible Total
        ('VIRFA', c_uint32),  # VI Resources Flexible Assigned
        ('VIRFAP', c_uint16),  # VI Resources Flexible Allocated to Primary
        ('VIPRT', c_uint16),  # VI Resources Private Total
        ('VIFRSM', c_uint16),  # VI Resources Flexible Secondary Maximum
        ('VIGRAN', c_uint16),  # VI Flexible Resource Preferred Granularity
        ('RSV2', c_uint8 * 4016),  # NVM Set Attributes Entry
    ]
    desc = {
        'CNTLID': 'Controller Identifier', 'PORTID': 'Port Identifier', 'CRT': 'Controller Resource Types',
        'VQFRT': 'VQ Resources Flexible Total', 'VQRFA': 'VQ Resources Flexible Assigned',
        'VQRFAP': 'VQ Resources Flexible Allocated to Primary', 'VQPRT': 'VQ Resources Private Total',
        'VQFRSM': 'VQ Resources Flexible Secondary Maximum', 'VQGRAN': 'VQ Flexible Resource Preferred Granularity',
        'VIFRT': 'VI Resources Flexible Total', 'VIFRA': 'VI Resources Flexible Assigned',
        'VIRFAP': 'VI Resources Flexible Allocated to Primary', 'VIPRT': 'VI Resources Private Total',
        'VIFRSM': 'I Resources Flexible Secondary Maximum', 'VIGRAN': 'VI Flexible Resource Preferred Granularity'
    }


class SecondaryControllerListEntry(Structure):
    """Identify - SecondaryControllerListEntry Data Structure"""
    _pack_ = 1
    _fields_ = [
        ('SCID', c_uint16),  # Secondary Controller Identifier
        ('PCID', c_uint16),  # Primary Controller Identifier
        ('SCS', c_uint8),  # Secondary Controller State
        ('RSV0', c_uint8 * 3),
        ('VFN', c_uint16),  # Virtual Function Number
        ('NVQ', c_uint16),  # Number of VQ Flexible Resources Assigned
        ('NVI', c_uint16),  # Number of VI Flexible Resources Assigned
        ('RSV1', c_uint8 * 18),
    ]
    desc = {
        'SCID': 'Secondary Controller Identifier', 'PCID': 'Primary Controller Identifier',
        'SCS': 'Secondary Controller State', 'VFN': 'Virtual Function Number',
        'NVQ': 'Number of VQ Flexible Resources Assigned', 'NVI': 'Number of VI Flexible Resources Assigned'
    }


class SecondaryControllerList(Structure):
    """Identify - SecondaryControllerList Data Structure"""
    _pack_ = 1
    _fields_ = [
        ('NI', c_uint8),  # Number of Identifiers
        ('RSV0', c_uint8 * 31),
        ('ENTRY', SecondaryControllerListEntry * 127),  # Secondary Controller List
    ]
    desc = {
        'NI': 'Number of Identifiers', 'ENTRY': 'Secondary Controller List',
    }


class NamespaceList(Structure):
    _pack_ = 1
    _fields_ = [
        ('ID', c_uint32 * 1024),  # Namespace ID
    ]
    desc = {
        'ID': 'Namespace ID'
    }


class ControllerList(Structure):
    _pack_ = 1
    _fields_ = [
        ('NUM', c_uint16),  # Number of Identifiers
        ('ID', c_uint16 * 2047),  # Controller ID
    ]
    desc = {
        'NUM': 'Number of Identifiers', 'ID': 'Controller ID'
    }


IDENTIFY_CNS = {
    0x0: NamespaceDataStructure,
    0x1: ControllerDataStructure,
    0x2: NamespaceList,
    0x10: NamespaceList,
    0x11: NamespaceDataStructure,
    0x12: ControllerList,
    0x13: ControllerList,
    0x14: PrimaryControllerCap,
    0x15: SecondaryControllerList,
}
