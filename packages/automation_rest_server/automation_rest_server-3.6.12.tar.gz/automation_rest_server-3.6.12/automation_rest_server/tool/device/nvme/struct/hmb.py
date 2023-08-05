#!/usr/bin/env python
# pylint: disable=superfluous-parens,missing-docstring,too-few-public-methods
"""
Created on 20/1, 2021

@author: wwang
"""
from ctypes import Structure, c_uint32


class HMBEntry(Structure):
    _pack_ = 1
    _fields_ = [
        ('UTI', c_uint32, 6),
        ('RSV0', c_uint32, 26),
        ('LS', c_uint32, 32),
        ('CHI', c_uint32, 32),
        ('CHO', c_uint32, 32),
        ('CTI', c_uint32, 32),
        ('CTO', c_uint32, 32),
        ('RSVD1', c_uint32, 32)
    ]
    desc = {
        'UTI': 'The Tenant ID that uses HMB',
        'LS': 'The lease size of this tenant',
        'CHI': 'Head index in HMB descriptor list entry',
        'CHO': 'Head offset to the start address of the head index',
        'CTI': 'Tail index in HMB descriptor list entry',
        'CT0': 'Tail offset to the start address of the tail index',
    }


class HMB(Structure):
    """HMB"""
    _pack_ = 1
    _fields_ = [
        ('Tenant id', HMBEntry * 14)  # Tenant Info for ID
    ]
    desc = {
        'Tenant id': 'Tenant Info for ID '
    }
