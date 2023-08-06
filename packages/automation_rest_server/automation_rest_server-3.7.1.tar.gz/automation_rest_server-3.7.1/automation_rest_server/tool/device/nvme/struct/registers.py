#!/usr/bin/env python
# pylint: disable=superfluous-parens,missing-docstring,too-few-public-methods
"""
Created on 2020/06/10

@author: yyang
"""
from ctypes import Structure, c_uint8, c_uint16, c_uint32


class ID(Structure):
    _pack_ = 1
    _fields_ = [
        ('VID', c_uint32, 16),  # Vendor ID (VID)
        ('DID', c_uint32, 16),  # Device ID (DID)
    ]
    desc = {'VID': 'Vendor ID', 'DID': 'Device ID'}


class CMD(Structure):
    _pack_ = 1
    _fields_ = [
        ('IOSE', c_uint16, 1),  # I/O Space Enable (IOSE)
        ('MSE', c_uint16, 1),  # Memory Space Enable (MSE)
        ('BME', c_uint16, 1),  # Bus Master Enable (BME)
        ('SCE', c_uint16, 1),  # Special Cycle Enable (SCE)
        ('MWIE', c_uint16, 1),  # Memory Write and Invalidate Enable (MWIE)
        ('VGA', c_uint16, 1),  # VGA Palette Snooping Enable (VGA)
        ('PEE', c_uint16, 1),  # Parity Error Response Enable (PEE)
        ('HW', c_uint16, 1),  # Hardwired
        ('SEE', c_uint16, 1),  # SERR# Enable (SEE)
        ('FBE', c_uint16, 1),  # Fast Back-to-Back Enable (FBE)
        ('ID', c_uint16, 1),  # Interrupt Disable (ID)
        ('RSV', c_uint16, 5),
    ]
    desc = {
        'IOSE': 'I/O Space Enable', 'MSE': 'Memory Space Enable', 'BME': 'Bus Master Enable',
        'SCE': 'Special Cycle Enable', 'MWIE': 'Memory Write and Invalidate Enable',
        'VGA': 'VGA Palette Snooping Enable', 'PEE': 'Parity Error Response Enable', 'HW': 'Hardwired',
        'SEE': 'SERR# Enable', 'FBE': 'Fast Back-to-Back Enable', 'ID': 'Interrupt Disable'
    }


class STS(Structure):
    _pack_ = 1
    _fields_ = [
        ('RSV0', c_uint16, 3),
        ('IS', c_uint16, 1),  # Interrupt Status (IS)
        ('CL', c_uint16, 1),  # Capabilities List (CL)
        ('C66', c_uint16, 1),  # 66 MHz Capable (C66)
        ('RSV1', c_uint16, 1),
        ('FBC', c_uint16, 1),  # Fast Back-to-Back Capable (FBC)
        ('DPD', c_uint16, 1),  # Master Data Pariy Error Detected (DPD)
        ('DEVT', c_uint16, 2),  # DEVSEL# Timing (DEVT)
        ('STA', c_uint16, 1),  # Signaled Target-Abort (STA)
        ('RTA', c_uint16, 1),  # Received Target Abort (RTA)
        ('RMA', c_uint16, 1),  # Received Master-Abort (RMA)
        ('SSE', c_uint16, 1),  # Signaled System Error (SSE)
        ('DPE', c_uint16, 1),  # Detected Parity Error (DPE)
    ]
    desc = {
        'IS': 'Interrupt Status', 'CL': 'Capabilities List', 'C66': '66 MHz Capable',
        'FBC': 'Fast Back-to-Back Capable', 'DPD': 'Master Data Pariy Error Detected', 'DEVT': 'DEVSEL# Timing',
        'STA': 'Signaled Target-Abort', 'RTA': 'Received Target Abort', 'RMA': 'Received Master-Abort',
        'SSE': 'Signaled System Error', 'DPE': 'Detected Parity Error',
    }


class CC(Structure):
    _pack_ = 1
    _fields_ = [
        ('PI', c_uint8),  # Programming Interface (PI)
        ('SCC', c_uint8),  # Sub Class Code (SCC)
        ('BCC', c_uint8),  # Base Class Code (BCC)
    ]
    desc = {'PI': 'Programming Interface', 'SCC': 'Sub Class Code', 'BCC': 'Base Class Code'}


class HTYPE(Structure):
    _pack_ = 1
    _fields_ = [
        ('HL', c_uint8, 7),  # Header Layout (HL)
        ('MFD', c_uint8, 1),  # Multi-Function Device (MFD)
    ]
    desc = {'HL': 'Header Layout', 'MFD': 'Multi-Function Device'}


class BIST(Structure):
    _pack_ = 1
    _fields_ = [
        ('CC', c_uint8, 4),  # Completion Code (CC)
        ('RSV', c_uint8, 2),
        ('SB', c_uint8, 1),  # Start BIST (SB)
        ('BC', c_uint8, 1),  # BIST Capable (BC)
    ]
    desc = {'CC': 'Completion Code', 'SB': 'Start BIST', 'BC': 'BIST Capable'}


class MLBAR(Structure):
    _pack_ = 1
    _fields_ = [
        ('RTE', c_uint32, 1),  # Resource Type Indicator (RTE)
        ('TP', c_uint32, 2),  # Type (TP)
        ('PF', c_uint32, 1),  # Prefetchable (PF)
        ('RSV', c_uint32, 10),
        ('BA', c_uint32, 18),  # Base Address (BA)
    ]
    desc = {'RTE': 'Resource Type Indicator', 'TP': 'Type', 'PF': 'Prefetchable', 'BA': 'Base Address'}


class BAR(Structure):
    _pack_ = 1
    _fields_ = [
        ('RTE', c_uint32, 1),  # Resource Type Indicator (RTE)
        ('RSV', c_uint32, 2),
        ('BA', c_uint32, 29),  # Base Address (BA)
    ]
    desc = {'RTE': 'Resource Type Indicator', 'BA': 'Base Address'}


class SS(Structure):
    _pack_ = 1
    _fields_ = [
        ('SSVID', c_uint32, 16),  # Subsystem Vendor ID (SSVID)
        ('SSID', c_uint32, 16),  # Subsystem ID (SSID)
    ]
    desc = {'SSVID': 'Subsystem Vendor ID', 'SSID': 'Subsystem ID'}


class INTR(Structure):
    _pack_ = 1
    _fields_ = [
        ('ILINE', c_uint16, 8),  # Interrupt Line (ILINE)
        ('IPIN', c_uint16, 8),  # Interrupt Pin (IPIN)
    ]
    desc = {'ILINE': 'Interrupt Line', 'IPIN': 'Interrupt Pin'}


class PCIHeader(Structure):
    """System Bus (PCI Express) Registers - PCI Header"""
    _pack_ = 1
    _fields_ = [
        ('ID', ID),  # Identifiers
        ('CMD', CMD),  # Command Register
        ('STS', STS),  # Device Status
        ('RID', c_uint8),  # Revision ID
        ('CC', CC),  # Class Codes
        ('CLS', c_uint8),  # Cache Line Size
        ('MLT', c_uint8),  # Master Latency Timer
        ('HTYPE', HTYPE),  # Header Type
        ('BIST', BIST),  # Built In Self Test (Optional)
        ('MLBAR', MLBAR),  # Memory Register Base Address, lower 32-bits <BAR0>
        ('MUBAR', c_uint32),  # Memory Register Base Address, upper 32-bits <BAR1>
        ('BAR2', BAR),  # Refer to section 2.1.12
        ('BAR3', c_uint32),  # Vendor Specific
        ('BAR4', c_uint32),  # Vendor Specific
        ('BAR5', c_uint32),  # Vendor Specific
        ('CCPTR', c_uint32),  # CardBus CIS Pointer
        ('SS', SS),  # Subsystem Identifiers
        ('EROM', c_uint32),  # Expansion ROM Base Address (Optional)
        ('CAP', c_uint8),  # Capabilities Pointer
        ('RSV', c_uint8 * 7),  #
        ('INTR', INTR),  # Interrupt Information
        ('MGNT', c_uint8),  # Minimum Grant (Optional)
        ('MLAT', c_uint8),  # Maximum Latency (Optional)
    ]
    desc = {
        'RID': 'Revision ID', 'CLS': 'Cache Line Size', 'MLT': 'Master Latency Timer', 'MUBAR': 'BAR1 Address',
        'BAR3': 'BAR3 Address', 'BAR4': 'BAR4 Address', 'BAR5': 'BAR5 Address', 'CCPTR': 'CardBus CIS Pointer',
        'EROM': 'Expansion ROM Base Address', 'CAP': 'Capabilities Pointer', 'MGNT': 'Minimum Grant',
        'MLAT': 'Maximum Latency',
    }


class PID(Structure):
    _pack_ = 1
    _fields_ = [
        ('CID', c_uint16, 8),  # Cap ID (CID)
        ('NEXT', c_uint16, 8),  # Next Capability (NEXT)
    ]
    desc = {'CID': 'Capability ID', 'NEXT': 'Next Capability'}


class PC(Structure):
    _pack_ = 1
    _fields_ = [
        ('VS', c_uint16, 3),  # Version (VS)
        ('PMEC', c_uint16, 1),  # PME Clock (PMEC)
        ('RSV', c_uint16, 1),
        ('DSI', c_uint16, 1),  # Device Specific Initialization (DSI)
        ('AUXC', c_uint16, 3),  # Aux_Current (AUXC)
        ('D1S', c_uint16, 1),  # D1_Support (D1S)
        ('D2S', c_uint16, 1),  # D2_Support (D2S)
        ('PSUP', c_uint16, 5),  # PME_Support (PSUP)
    ]
    desc = {
        'VS': 'Version', 'PMEC': 'PME Clock', 'DSI': 'Device Specific Initialization',
        'AUXC': 'Aux_Current', 'D1S': 'D1_Support', 'D2S': 'D2_Support', 'PSUP': 'PME_Support'
    }


class PMCS(Structure):
    _pack_ = 1
    _fields_ = [
        ('PS', c_uint16, 2),  # Power State (PS)
        ('RSV1', c_uint16, 1),
        ('NSFRST', c_uint16, 1),  # No Soft Reset (NSFRST)
        ('RSV2', c_uint16, 4),
        ('PMEE', c_uint16, 1),  # PME Enable (PMEE)
        ('DSE', c_uint16, 4),  # Data Select (DSE)
        ('DSC', c_uint16, 2),  # Data Scale (DSC)
        ('PMES', c_uint16, 1),  # PME Status (PMES)
    ]
    desc = {
        'PS': 'Power State', 'NSFRST': 'No Soft Reset', 'PMEE': 'PME Enable',
        'DSE': 'Data Select', 'DSC': 'Data Scale', 'PMES': 'PME Status'
    }


class PMCAP(Structure):
    """System Bus (PCI Express) Registers - PCI Power Management Capabilities"""
    _pack_ = 1
    _fields_ = [
        ('PID', PID),  # PCI Power Management Capability ID
        ('PC', PC),  # PCI Power Management Capabilities
        ('PMCS', PMCS),  # PCI Power Management Control and Status
    ]
    desc = {
        'PID': 'PCI Power Management Capability ID', 'PC': 'PCI Power Management Capabilities',
        'PMCS': 'PCI Power Management Control and Status'
    }


class MID(Structure):
    _pack_ = 1
    _fields_ = [
        ('CID', c_uint16, 8),  # Capability ID (CID)
        ('NEXT', c_uint16, 8),  # Next Pointer (NEXT)
    ]
    desc = {'CID': 'Capability ID', 'NEXT': 'Next Pointer'}


class MC(Structure):
    _pack_ = 1
    _fields_ = [
        ('MSIE', c_uint16, 1),  # MSI Enable (MSIE)
        ('MMC', c_uint16, 3),  # Multiple Message Capable (MMC)
        ('MME', c_uint16, 3),  # Multiple Message Enable (MME)
        ('C64', c_uint16, 1),  # 64 Bit Address Capable (C64)
        ('PVM', c_uint16, 1),  # Per-Vector Masking Capable (PVM)
        ('RSV', c_uint16, 7),
    ]
    desc = {
        'MSIE': 'MSI Enable', 'MCC': 'Multiple Message Capable', 'MME': 'Multiple Message Enable',
        'C64': '64 Bit Address Capable', 'PVM': 'Per-Vector Masking Capable'
    }


class MA(Structure):
    _pack_ = 1
    _fields_ = [
        ('RSV', c_uint32, 2),
        ('ADDR', c_uint32, 30),  # Address (ADDR)
    ]
    desc = {'ADDR': 'Message Signaled Interrupt Message Address'}


class MSICAP(Structure):
    """System Bus (PCI Express) Registers - Message Signaled Interrupt Capability (Optional)"""
    _pack_ = 1
    _fields_ = [
        ('MID', MID),  # Message Signaled Interrupt Identifiers
        ('MC', MC),  # Message Signaled Interrupt Message Control
        ('MA', MA),  # Message Signaled Interrupt Message Address
        ('MUA', c_uint32),  # Message Signaled Interrupt Upper Address
        ('MD', c_uint16),  # Message Signaled Interrupt Message Data
        ('RSV', c_uint16),
        ('MMASK', c_uint32),  # Message Signaled Interrupt Mask Bits (Optional)
        ('MPEND', c_uint32),  # Message Signaled Interrupt Pending Bits (Optional)
    ]
    desc = {
        'MUA': 'Message Signaled Interrupt Upper Address', 'MD': 'Message Signaled Interrupt Message Data',
        'MMASK': 'Message Signaled Interrupt Mask Bits', 'MPEND': 'Message Signaled Interrupt Pending Bits'
    }


class MIDX(Structure):
    _pack_ = 1
    _fields_ = [
        ('CID', c_uint16, 8),  # Capability ID (CID)
        ('NEXT', c_uint16, 8),  # Next Pointer (NEXT)
    ]
    desc = {'CID': 'Capability ID', 'NEXT': 'Next Pointer'}


class MXC(Structure):
    _pack_ = 1
    _fields_ = [
        ('TS', c_uint16, 11),  # Table Size (TS)
        ('RSV', c_uint16, 3),
        ('FM', c_uint16, 1),  # Function Mask (FM)
        ('MXE', c_uint16, 1),  # MSI-X Enable (MXE)
    ]
    desc = {'TS': 'Table Size', 'FM': 'Function Mask', 'MXE': 'MSI-X Enable'}


class MTAB(Structure):
    _pack_ = 1
    _fields_ = [
        ('TBIR', c_uint32, 3),  # Table BIR (TBIR)
        ('TO', c_uint32, 29),  # Table Offset (TO)
    ]
    desc = {'TBIR': 'Table BIR', 'TO': 'Table Offset'}


class MPBA(Structure):
    _pack_ = 1
    _fields_ = [
        ('PBIR', c_uint32, 3),  # PBA Offset (PBAO)
        ('PBAO', c_uint32, 29),  # PBA BIR (PBIR)
    ]
    desc = {'TBIR': 'Table BIR', 'TO': 'Table Offset'}


class MSIXCAP(Structure):
    """System Bus (PCI Express) Registers - MSI-X Capability (Optional)"""
    _pack_ = 1
    _fields_ = [
        ('MIDX', MIDX),  # MSI-X Identifiers
        ('MXC', MXC),  # MSI-X Message Control
        ('MTAB', MTAB),  # MSI-X Table Offset / Table BIR
        ('MPBA', MPBA),  # MSI-X PBA Offset / PBA BIR
    ]
    desc = {
        'MIDX': 'MSI-X Identifiers', 'MXC': 'MSI-X Message Control',
        'MTAB': 'MSI-X Table Offset / Table BIR', 'MPBA': 'MSI-X PBA Offset / PBA BIR'
    }


class PXID(Structure):
    _pack_ = 1
    _fields_ = [
        ('CID', c_uint16, 3),  # Capability ID (CID)
        ('NEXT', c_uint16, 29),  # Next Pointer (NEXT)
    ]
    desc = {'CID': 'Capability ID', 'NEXT': 'Next Pointer'}


class PXCAP(Structure):
    _pack_ = 1
    _fields_ = [
        ('VER', c_uint16, 4),  # Capability Version (VER)
        ('DPT', c_uint16, 4),  # Device/Port Type (DPT)
        ('SI', c_uint16, 1),  # Slot Implemented (SI)
        ('IMN', c_uint16, 5),  # Interrupt Message Number (IMN)
        ('RSV', c_uint16, 2),
    ]
    desc = {
        'VER': 'Capability Version', 'DPT': 'Device/Port Type',
        'SI': 'Slot Implemented', 'IMN': 'Interrupt Message Number'
    }


class PXDCAP(Structure):
    _pack_ = 1
    _fields_ = [
        ('MPS', c_uint32, 3),  # Max_Payload_Size Supported (MPS)
        ('PFS', c_uint32, 2),  # Phantom Functions Supported (PFS)
        ('ETFS', c_uint32, 1),  # Extended Tag Field Supported (ETFS)
        ('L0SL', c_uint32, 3),  # Endpoint L0s Acceptable Latency (L0SL)
        ('L1L', c_uint32, 3),  # Endpoint L1 Acceptable Latency (L1L)
        ('RSV0', c_uint32, 3),
        ('RER', c_uint32, 1),  # Role-based Error Reporting (RER)
        ('RSV1', c_uint32, 2),
        ('CSPLV', c_uint32, 8),  # Captured Slot Power Limit Value (CSPLV)
        ('CSPLS', c_uint32, 2),  # Captured Slot Power Limit Scale (CSPLS)
        ('FLRC', c_uint32, 1),  # Function Level Reset Capability (FLRC)
        ('RSV2', c_uint32, 3),
    ]
    desc = {
        'MPS': 'Max_Payload_Size Supported', 'PFS': 'Phantom Functions Supported',
        'ETFS': 'Extended Tag Field Supported', 'L0SL': 'Endpoint L0s Acceptable Latency',
        'L1L': 'Endpoint L1 Acceptable Latency', 'RER': 'Role-based Error Reporting',
        'CSPLV': 'Captured Slot Power Limit Value', 'CSPLS': 'Captured Slot Power Limit Scale',
        'FLRC': 'Function Level Reset Capability'
    }


class PXDC(Structure):
    _pack_ = 1
    _fields_ = [
        ('CERE', c_uint16, 1),  # Correctable Error Reporting Enable (CERE)
        ('NFERE', c_uint16, 1),  # Non-Fatal Error Reporting Enable (NFERE)
        ('FERE', c_uint16, 1),  # Fatal Error Reporting Enable (FERE)
        ('URRE', c_uint16, 1),  # Unsupported Request Reporting Enable (URRE)
        ('ERO', c_uint16, 1),  # Enable Relaxed Ordering (ERO)
        ('MPS', c_uint16, 3),  # Max_Payload_Size (MPS)
        ('ETE', c_uint16, 1),  # Extended Tag Enable (ETE)
        ('PFE', c_uint16, 1),  # Phantom Functions Enable (PFE)
        ('APPME', c_uint16, 1),  # AUX Power PM Enable (APPME)
        ('ENS', c_uint16, 1),  # Enable No Snoop (ENS)
        ('MRRS', c_uint16, 3),  # Max_Read_Request_Size (MRRS)
        ('IFLR', c_uint16, 1),  # Initiate Function Level Reset
    ]
    desc = {
        'CERE': 'Correctable Error Reporting Enable', 'NFERE': 'Non-Fatal Error Reporting Enable',
        'FERE': 'Fatal Error Reporting Enable', 'URRE': 'Unsupported Request Reporting Enable',
        'ERO': 'Enable Relaxed Ordering', 'MPS': 'Max Payload Size', 'ETE': 'Extended Tag Enable',
        'PFE': 'Phantom Functions Enable', 'APPME': 'AUX Power PM Enable', 'ENS': 'Enable No Snoop',
        'MRRS': 'Max_Read_Request_Size', 'IFLR': 'Initiate Function Level Reset',
    }


class PXDS(Structure):
    _pack_ = 1
    _fields_ = [
        ('CED', c_uint16, 1),  # Correctable Error Detected (CED)
        ('NFED', c_uint16, 1),  # Non-Fatal Error Detected (NFED)
        ('FED', c_uint16, 1),  # Fatal Error Detected (FED)
        ('URD', c_uint16, 1),  # Unsupported Request Detected (URD)
        ('APD', c_uint16, 1),  # AUX Power Detected (APD)
        ('TP', c_uint16, 1),  # Transactions Pending (TP)
        ('RSV', c_uint16, 10),
    ]
    desc = {
        'CED': 'Correctable Error Detected', 'NFED': 'Non-Fatal Error Detected', 'FED': 'Fatal Error Detected',
        'URD': 'Unsupported Request Detected', 'APD': 'AUX Power Detected', 'TP': 'Transactions Pending'
    }


class PXLCAP(Structure):
    _pack_ = 1
    _fields_ = [
        ('SLS', c_uint32, 4),  # Supported Link Speeds (SLS)
        ('MLW', c_uint32, 6),  # Maximum Link Width (MLW)
        ('ASPMS', c_uint32, 2),  # Active State Power Management Support (ASPMS)
        ('L0SEL', c_uint32, 3),  # L0s Exit Latency (L0SEL)
        ('L1EL', c_uint32, 3),  # L1 Exit Latency (L1EL)
        ('CPM', c_uint32, 1),  # Clock Power Management (CPM)
        ('SDERC', c_uint32, 1),  # Surprise Down Error Reporting Capable (SDERC)
        ('DLLLA', c_uint32, 1),  # Data Link Layer Link Active Reporting Capable (DLLLA)
        ('LBNC', c_uint32, 1),  # Link Bandwidth Notification Capability (LBNC)
        ('AOC', c_uint32, 1),  # ASPM Optionality Compliance (AOC)
        ('RSV', c_uint32, 1),  #
        ('PN', c_uint32, 8),  # Port Number (PN)
    ]
    desc = {
        'SLS': 'Supported Link Speeds', 'MLW': 'Maximum Link Width', 'ASPMS': 'Active State Power Management Support',
        'L0SEL': 'L0s Exit Latency', 'L1EL': 'L1 Exit Latency', 'CPM': 'Clock Power Management',
        'SDERC': 'Surprise Down Error Reporting Capable', 'DLLLA': 'Data Link Layer Link Active Reporting Capable',
        'LBNC': 'Link Bandwidth Notification Capability', 'AOC': 'ASPM Optionality Compliance', 'PN': 'Port Number'
    }


class PXLC(Structure):
    _pack_ = 1
    _fields_ = [
        ('ASPMC', c_uint16, 2),  # Active State Power Management Control (ASPMC)
        ('RSV0', c_uint16, 1),
        ('RCB', c_uint16, 1),  # Read Completion Boundary (RCB)
        ('RSV1', c_uint16, 2),
        ('CCC)', c_uint16, 1),  # Common Clock Configuration (CCC)
        ('ES', c_uint16, 1),  # Extended Synch (ES)
        ('ECPM', c_uint16, 1),  # Enable Clock Power Management (ECPM)
        ('HAWD', c_uint16, 1),  # Hardware Autonomous Width Disable (HAWD)
        ('RSV2', c_uint16, 6),
    ]
    desc = {
        'ASPMC': 'Active State Power Management Control', 'RCB': 'Read Completion Boundary',
        'CCC': 'Common Clock Configuration', 'ES': 'Extended Synch',
        'ECPM': 'Enable Clock Power Management', 'HAWD': 'Hardware Autonomous Width Disable',
    }


class PXLS(Structure):
    _pack_ = 1
    _fields_ = [
        ('CLS', c_uint16, 4),  # Current Link Speed
        ('NLW', c_uint16, 6),  # Negotiated Link Width
        ('RSV1', c_uint16, 2),  # Reserved
        ('SCC', c_uint16, 1),  # Slot Clock Configuration
        ('RSV0', c_uint16, 3),  # Reserved
    ]
    desc = {
        'CLS': 'Current Link Speed ', 'NLW': 'Negotiated Link Width ', 'SCC': 'Slot Clock Configuration'
    }


class PXDCAP2(Structure):
    _pack_ = 1
    _fields_ = [
        ('CTRS', c_uint32, 4),  # Completion Timeout Ranges Supported
        ('CTDS', c_uint32, 1),  # Completion Timeout Disable Supported
        ('ARIFS', c_uint32, 1),  # ARI Forwarding Supported
        ('AORS', c_uint32, 1),  # AtomicOp Routing Supported
        ('32AOCS', c_uint32, 1),  # 32-bit AtomicOp Completer Supported
        ('64AOCS', c_uint32, 1),  # 64-bit AtomicOp Completer Supported
        ('128CCS', c_uint32, 1),  # 128-bit CAS Completer Supported
        ('NPRPR', c_uint32, 1),  # No RO-enabled PR-PR Passing
        ('LTRS', c_uint32, 1),  # Latency Tolerance Reporting Supported
        ('TPHCS', c_uint32, 2),  # TPH Completer Supported
        ('RSV1', c_uint32, 4),  # Reserved
        ('OBFFS', c_uint32, 2),  # OBFF Supported
        ('EFFS', c_uint32, 1),  # Extended Fmt Field Supported
        ('EETPS', c_uint32, 1),  # End-End TLP Prefix Supported
        ('MEETP', c_uint32, 2),  # Max End-End TLP Prefixes
        ('RSV0', c_uint32, 1),  # Reserved
    ]
    desc = {
        'CTRS': 'Completion Timeout Ranges Supported ', 'CTDS': 'Completion Timeout Disable Supported ',
        'ARIFS': 'ARI Forwarding Supported ', 'AORS': 'AtomicOp Routing Supported ',
        '32AOCS': '32-bit AtomicOp Completer Supported ', '64AOCS': '64-bit AtomicOp Completer Supported ',
        '128CCS': '128-bit CAS Completer Supported ', 'NPRPR': 'No RO-enabled PR-PR Passing ',
        'LTRS': 'Latency Tolerance Reporting Supported ', 'TPHCS': 'TPH Completer Supported ',
        'OBFFS': 'OBFF Supported ', 'EFFS': 'Extended Fmt Field Supported ', 'EETPS': 'End-End TLP Prefix Supported ',
        'MEETP': 'Max End-End TLP Prefixes '
    }


class PXDC2(Structure):
    _pack_ = 1
    _fields_ = [
        ('CTV', c_uint32, 4),  # Completion Timeout Value
        ('CTD', c_uint32, 1),  # Completion Timeout Disable
        ('RSV2', c_uint32, 5),  # Reserved
        ('LTRME', c_uint32, 1),  # Latency Tolerance Reporting Mechanism Enable
        ('RSV1', c_uint32, 2),  # Reserved
        ('OBFFE', c_uint32, 2),  # OBFF Enable
        ('RSV0', c_uint32, 1),  # Reserved
    ]
    desc = {
        'CTV': 'Completion Timeout Value', 'CTD': 'Completion Timeout Disable ',
        'LTRME': 'Latency Tolerance Reporting Mechanism Enable ', 'OBFFE': 'OBFF Enable '
    }


class PCIECAP(Structure):
    """System Bus (PCI Express) Registers - PCI Express Capability"""
    _pack_ = 1
    _fields_ = [
        ('PXID', PXID),  # PCI Express Capability ID
        ('PXCAP', PXCAP),  # PCI Express Capabilities
        ('PXDCAP', PXDCAP),  # PCI Express Device Capabilities
        ('PXDC', PXDC),  # PCI Express Device Control
        ('PXDS', PXDS),  # PCI Express Device Status
        ('PXLCAP', PXLCAP),  # PCI Express Link Capabilities
        ('PXLC', PXLC),  # PCI Express Link Control
        ('PXLS', PXLS),  # PCI Express Link Status
        ('PXDCAP2', PXDCAP2),  # PCI Express Device Capabilities 2
        ('PXDC2', PXDC2),  # PCI Express Device Control 2
    ]
    desc = {
        'PXID': 'PCI Express Capability ID', 'PXCAP': 'PCI Express Capabilities',
        'PXDCAP': 'PCI Express Device Capabilities', 'PXDC': 'PCI Express Device Control',
        'PXDS': 'PCI Express Device Status', 'PXLCAP': 'PCI Express Link Capabilities',
        'PXLC': 'PCI Express Link Control', 'PXLS': 'PCI Express Link Status',
        'PXDCAP2': 'PCI Express Device Capabilities 2', 'PXDC2': 'PCI Express Device Control 2',
    }


class AERID(Structure):
    _pack_ = 1
    _fields_ = [
        ('CID', c_uint32, 16),  # Capability ID
        ('CVER', c_uint32, 4),  # Capability Version
        ('NEXT', c_uint32, 1),  # Next Pointer
    ]
    desc = {
        'CID': 'Capability ID ', 'CVER': 'Capability Version ', 'NEXT': 'Next Pointer '
    }


class AERUCES(Structure):
    _pack_ = 1
    _fields_ = [
        ('RSV2', c_uint32, 4),  # Reserved
        ('DLPES', c_uint32, 1),  # Data Link Protocol Error Status
        ('RSV1', c_uint32, 7),  # Reserved
        ('PTS', c_uint32, 1),  # Poisoned TLP Status
        ('FCPES', c_uint32, 1),  # Flow Control Protocol Error Status
        ('CTS', c_uint32, 1),  # Completion Timeout Status
        ('CAS', c_uint32, 1),  # Completer Abort Status
        ('UCS', c_uint32, 1),  # Unexpected Completion Status
        ('ROS', c_uint32, 1),  # Receiver Overflow Status
        ('MTS', c_uint32, 1),  # Malformed TLP Status
        ('ECRCES', c_uint32, 1),  # ECRC Error Status
        ('URES', c_uint32, 1),  # Unsupported Request Error Status
        ('ACSVS', c_uint32, 1),  # ACS Violation Status
        ('UIES', c_uint32, 1),  # Uncorrectable Internal Error Status
        ('MCBTS', c_uint32, 1),  # MC Blocked TLP Status
        ('AOEBS', c_uint32, 1),  # AtomicOp Egress Blocked Status
        ('TPBES', c_uint32, 1),  # TLP Prefix Blocked Error Status
        ('RSV0', c_uint32, 1),  # Reserved
    ]
    desc = {
        'DLPES': 'Data Link Protocol Error Status ', 'PTS': 'Poisoned TLP Status ',
        'FCPES': 'Flow Control Protocol Error Status ', 'CTS': 'Completion Timeout Status ',
        'CAS': 'Completer Abort Status ', 'UCS': 'Unexpected Completion Status ', 'ROS': 'Receiver Overflow Status ',
        'MTS': 'Malformed TLP Status ', 'ECRCES': 'ECRC Error Status ', 'URES': 'Unsupported Request Error Status ',
        'ACSVS': 'ACS Violation Status ', 'UIES': 'Uncorrectable Internal Error Status ',
        'MCBTS': 'MC Blocked TLP Status ', 'AOEBS': 'AtomicOp Egress Blocked Status ',
        'TPBES': 'TLP Prefix Blocked Error Status '
    }


class AERUCEM(Structure):
    _pack_ = 1
    _fields_ = [
        ('RSV2', c_uint32, 4),  # Reserved
        ('DLPEM', c_uint32, 1),  # Data Link Protocol Error Mask
        ('RSV1', c_uint32, 7),  # Reserved
        ('PTM', c_uint32, 1),  # Poisoned TLP Mask
        ('FCPEM', c_uint32, 1),  # Flow Control Protocol Error Mask
        ('CTM', c_uint32, 1),  # Completion Timeout Mask
        ('CAM', c_uint32, 1),  # Completer Abort Mask
        ('UCM', c_uint32, 1),  # Unexpected Completion Mask
        ('ROM', c_uint32, 1),  # Receiver Overflow Mask
        ('MTM', c_uint32, 1),  # Malformed TLP Mask
        ('ECRCEM', c_uint32, 1),  # ECRC Error Mask
        ('UREM', c_uint32, 1),  # Unsupported Request Error Mask
        ('ACSVM', c_uint32, 1),  # ACS Violation Mask
        ('UIEM', c_uint32, 1),  # Uncorrectable Internal Error Mask
        ('MCBTM', c_uint32, 1),  # MC Blocked TLP Mask
        ('AOEBM', c_uint32, 1),  # AtomicOp Egress Blocked Mask
        ('TPBEM', c_uint32, 1),  # TLP Prefix Blocked Error Mask
        ('RSV0', c_uint32, 1),  # Reserved
    ]
    desc = {
        'DLPEM': 'Data Link Protocol Error Mask ', 'PTM': 'Poisoned TLP Mask ',
        'FCPEM': 'Flow Control Protocol Error Mask ', 'CTM': 'Completion Timeout Mask ', 'CAM': 'Completer Abort Mask ',
        'UCM': 'Unexpected Completion Mask ', 'ROM': 'Receiver Overflow Mask ', 'MTM': 'Malformed TLP Mask ',
        'ECRCEM': 'ECRC Error Mask ', 'UREM': 'Unsupported Request Error Mask ', 'ACSVM': 'ACS Violation Mask ',
        'UIEM': 'Uncorrectable Internal Error Mask ', 'MCBTM': 'MC Blocked TLP Mask ',
        'AOEBM': 'AtomicOp Egress Blocked Mask ', 'TPBEM': 'TLP Prefix Blocked Error Mask '
    }


class AERUCESEV(Structure):
    _pack_ = 1
    _fields_ = [
        ('RSV2', c_uint32, 4),  # Reserved
        ('DLPESEV', c_uint32, 1),  # Data Link Protocol Error Severity
        ('RSV1', c_uint32, 7),  # Reserved
        ('PTSEV', c_uint32, 1),  # Poisoned TLP Severity
        ('FCPESEV', c_uint32, 1),  # Flow Control Protocol Error Severity
        ('CTSEV', c_uint32, 1),  # Completion Timeout Severity
        ('CASEV', c_uint32, 1),  # Completer Abort Severity
        ('UCSEV', c_uint32, 1),  # Unexpected Completion Severity
        ('ROSEV', c_uint32, 1),  # Receiver Overflow Severity
        ('MTSEV', c_uint32, 1),  # Malformed TLP Severity
        ('ECRCESEV', c_uint32, 1),  # ECRC Error Severity
        ('URESEV', c_uint32, 1),  # Unsupported Request Error Severity
        ('ACSVSEV', c_uint32, 1),  # ACS Violation Severity
        ('UIESEV', c_uint32, 1),  # Uncorrectable Internal Error Severity
        ('MCBTSEV', c_uint32, 1),  # MC Blocked TLP Severity
        ('AOEBSEV', c_uint32, 1),  # AtomicOp Egress Blocked Severity
        ('TPBESEV', c_uint32, 1),  # TLP Prefix Blocked Error Severity
        ('RSV0', c_uint32, 1),  # Reserved
    ]
    desc = {
        'DLPESEV': 'Data Link Protocol Error Severity ', 'PTSEV': 'Poisoned TLP Severity ',
        'FCPESEV': 'Flow Control Protocol Error Severity ', 'CTSEV': 'Completion Timeout Severity ',
        'CASEV': 'Completer Abort Severity ', 'UCSEV': 'Unexpected Completion Severity ',
        'ROSEV': 'Receiver Overflow Severity ', 'MTSEV': 'Malformed TLP Severity ', 'ECRCESEV': 'ECRC Error Severity ',
        'URESEV': 'Unsupported Request Error Severity ', 'ACSVSEV': 'ACS Violation Severity ',
        'UIESEV': 'Uncorrectable Internal Error Severity ', 'MCBTSEV': 'MC Blocked TLP Severity ',
        'AOEBSEV': 'AtomicOp Egress Blocked Severity ', 'TPBESEV': 'TLP Prefix Blocked Error Severity '
    }


class AERCES(Structure):
    _pack_ = 1
    _fields_ = [
        ('RES', c_uint32, 1),  # Receiver Error Status
        ('RSV2', c_uint32, 5),  # Reserved
        ('BTS', c_uint32, 1),  # Bad TLP Status
        ('BDS', c_uint32, 1),  # Bad DLLP Status
        ('RRS', c_uint32, 1),  # REPLAY
        ('RSV1', c_uint32, 3),  # Reserved
        ('RTS', c_uint32, 1),  # Replay Timer Timeout Status
        ('ANFES', c_uint32, 1),  # Advisory Non-Fatal Error Status
        ('CIES', c_uint32, 1),  # Corrected Internal Error Status
        ('HLOS', c_uint32, 1),  # Header Log Overflow Status
        ('RSV0', c_uint32, 1),  # Reserved
    ]
    desc = {
        'RES': 'Receiver Error Status ', 'BTS': 'Bad TLP Status ', 'BDS': 'Bad DLLP Status ', 'RRS': 'REPLAY',
        'RTS': 'Replay Timer Timeout Status ', 'ANFES': 'Advisory Non-Fatal Error Status ',
        'CIES': 'Corrected Internal Error Status ', 'HLOS': 'Header Log Overflow Status '
    }


class AERCEM(Structure):
    _pack_ = 1
    _fields_ = [
        ('REM', c_uint32, 1),  # Receiver Error Mask
        ('RSV2', c_uint32, 5),  # Reserved
        ('BTM', c_uint32, 1),  # Bad TLP Mask
        ('BDM', c_uint32, 1),  # Bad DLLP Mask
        ('RRM', c_uint32, 1),  # REPLAY
        ('RSV1', c_uint32, 3),  # Reserved
        ('RTM', c_uint32, 1),  # Replay Timer Timeout Mask
        ('ANFEM', c_uint32, 1),  # Advisory Non-Fatal Error Mask
        ('CIEM', c_uint32, 1),  # Corrected Internal Error Mask
        ('HLOM', c_uint32, 1),  # Header Log Overflow Mask
        ('RSV0', c_uint32, 1),  # Reserved
    ]
    desc = {
        'REM': 'Receiver Error Mask ', 'BTM': 'Bad TLP Mask ', 'BDM': 'Bad DLLP Mask ', 'RRM': 'REPLAY',
        'RTM': 'Replay Timer Timeout Mask ', 'ANFEM': 'Advisory Non-Fatal Error Mask ',
        'CIEM': 'Corrected Internal Error Mask ', 'HLOM': 'Header Log Overflow Mask '
    }


class AERCC(Structure):
    _pack_ = 1
    _fields_ = [
        ('FEP', c_uint32, 5),  # First Error Pointer
        ('EGC', c_uint32, 1),  # ECRC Generation Capable
        ('EGE', c_uint32, 1),  # ECRC Generation Enable
        ('ECC', c_uint32, 1),  # ECRC Check Capable
        ('ECE', c_uint32, 1),  # ECRC Check Enable
        ('MHRC', c_uint32, 1),  # Multiple Header Recording Capable
        ('MHRE', c_uint32, 1),  # Multiple Header Recording Enable
        ('TPLP', c_uint32, 1),  # TLP Prefix Log Present
        ('RSV0', c_uint32, 1),  # Reserved
    ]
    desc = {
        'FEP': 'First Error Pointer ', 'EGC': 'ECRC Generation Capable ', 'EGE': 'ECRC Generation Enable ',
        'ECC': 'ECRC Check Capable ', 'ECE': 'ECRC Check Enable ', 'MHRC': 'Multiple Header Recording Capable ',
        'MHRE': 'Multiple Header Recording Enable ', 'TPLP': 'TLP Prefix Log Present '
    }


class AERHL(Structure):
    _pack_ = 1
    _fields_ = [
        ('HB3', c_uint8),  # Header Byte 3
        ('HB2', c_uint8),  # Header Byte 2
        ('HB1', c_uint8),  # Header Byte 1
        ('HB0', c_uint8),  # Header Byte 0
        ('HB7', c_uint8),  # Header Byte 7
        ('HB6', c_uint8),  # Header Byte 6
        ('HB5', c_uint8),  # Header Byte 5
        ('HB4', c_uint8),  # Header Byte 4
        ('HB11', c_uint8),  # Header Byte 11
        ('HB10', c_uint8),  # Header Byte 10
        ('HB9', c_uint8),  # Header Byte 9
        ('HB8', c_uint8),  # Header Byte 8
        ('HB15', c_uint8),  # Header Byte 15
        ('HB14', c_uint8),  # Header Byte 14
        ('HB13', c_uint8),  # Header Byte 13
        ('HB12', c_uint8),  # Header Byte 12
    ]
    desc = {
        'HB3': 'Header Byte 3 ', 'HB2': 'Header Byte 2 ', 'HB1': 'Header Byte 1 ', 'HB0': 'Header Byte 0 ',
        'HB7': 'Header Byte 7 ', 'HB6': 'Header Byte 6 ', 'HB5': 'Header Byte 5 ', 'HB4': 'Header Byte 4 ',
        'HB11': 'Header Byte 11 ', 'HB10': 'Header Byte 10 ', 'HB9': 'Header Byte 9 ', 'HB8': 'Header Byte 8 ',
        'HB15': 'Header Byte 15 ', 'HB14': 'Header Byte 14 ', 'HB13': 'Header Byte 13 ', 'HB12': 'Header Byte 12 '
    }


class AERTLP(Structure):
    _pack_ = 1
    _fields_ = [
        ('TPL1B3', c_uint8),  # First TLP Prefix Log Byte 3
        ('TPL1B2', c_uint8),  # First TLP Prefix Log Byte 2
        ('TPL1B1', c_uint8),  # First TLP Prefix Log Byte 1
        ('TPL1B0', c_uint8),  # First TLP Prefix Log Byte 0
        ('TPL2B3', c_uint8),  # Second TLP Prefix Log Byte 3
        ('TPL2B2', c_uint8),  # Second TLP Prefix Log Byte 2
        ('TPL2B1', c_uint8),  # Second TLP Prefix Log Byte 1
        ('TPL2B0', c_uint8),  # Second TLP Prefix Log Byte 0
        ('TPL3B3', c_uint8),  # Third TLP Prefix Log Byte 3
        ('TPL3B2', c_uint8),  # Third TLP Prefix Log Byte 2
        ('TPL3B1', c_uint8),  # Third TLP Prefix Log Byte 1
        ('TPL3B0', c_uint8),  # Third TLP Prefix Log Byte 0
        ('TPL4B3', c_uint8),  # Fourth TLP Prefix Log Byte 3
        ('TPL4B2', c_uint8),  # Fourth TLP Prefix Log Byte 2
        ('TPL4B1', c_uint8),  # Fourth TLP Prefix Log Byte 1
        ('TPL4B0', c_uint8),  # Fourth TLP Prefix Log Byte 0
    ]
    desc = {
        'TPL1B3': 'First TLP Prefix Log Byte 3 ', 'TPL1B2': 'First TLP Prefix Log Byte 2 ',
        'TPL1B1': 'First TLP Prefix Log Byte 1 ', 'TPL1B0': 'First TLP Prefix Log Byte 0 ',
        'TPL2B3': 'Second TLP Prefix Log Byte 3 ', 'TPL2B2': 'Second TLP Prefix Log Byte 2 ',
        'TPL2B1': 'Second TLP Prefix Log Byte 1 ', 'TPL2B0': 'Second TLP Prefix Log Byte 0 ',
        'TPL3B3': 'Third TLP Prefix Log Byte 3 ', 'TPL3B2': 'Third TLP Prefix Log Byte 2 ',
        'TPL3B1': 'Third TLP Prefix Log Byte 1 ', 'TPL3B0': 'Third TLP Prefix Log Byte 0 ',
        'TPL4B3': 'Fourth TLP Prefix Log Byte 3 ', 'TPL4B2': 'Fourth TLP Prefix Log Byte 2 ',
        'TPL4B1': 'Fourth TLP Prefix Log Byte 1 ', 'TPL4B0': 'Fourth TLP Prefix Log Byte 0 '
    }


class AERCAP(Structure):
    """System Bus (PCI Express) Registers - Advanced Error Reporting Capability (Optional)"""
    _pack_ = 1
    _fields_ = [
        ('AERID', AERID),  # AER Capability ID
        ('AERUCES', AERUCES),  # AER Uncorrectable Error Status Register
        ('AERUCEM', AERUCEM),  # AER Uncorrectable Error Mask Register
        ('AERUCESEV', AERUCESEV),  # AER Uncorrectable Error Severity Register
        ('AERCES', AERCES),  # AER Correctable Error Status Register
        ('AERCEM', AERCEM),  # AER Correctable Error Mask Register
        ('AERCC', AERCC),  # AER Advanced Error Capabilities and Control Reg
        ('AERHL', AERHL),  # AER Header Log Register
        ('AERTLP', AERTLP),  # AER TLP Prefix Log Register (Optional)
    ]
    desc = {
        'AERID': 'AER Capability ID', 'AERUCES': 'AER Uncorrectable Error Status Register',
        'AERUCEM': 'AER Uncorrectable Error Mask Register', 'AERUCESEV': 'AER Uncorrectable Error Severity Register',
        'AERCES': 'AER Correctable Error Status Register', 'AERCEM': 'AER Correctable Error Mask Register',
        'AERCC': 'AER Advanced Error Capabilities and Control Reg', 'AERHL': 'AER Header Log Register',
        'AERTLP': 'AER TLP Prefix Log Register'
    }
