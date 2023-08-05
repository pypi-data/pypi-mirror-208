#!/usr/bin/env python
# pylint: disable=superfluous-parens,missing-docstring,too-few-public-methods
"""
Created on Apr 19, 2019

@author: yyang
"""
from ctypes import Structure, c_uint16, c_uint32, c_uint64

class BLKSTAT():
    FREE = 0x00
    OPEN = 0x01
    CLOSE = 0x02
    RECYCLE = 0x06
    ERASE = 0x03
    PROTECT = 0x07

class TahoeBMIEntry(Structure):
    """bmi format"""
    _pack_ = 1
    _fields_ = [
        ('bm_st', c_uint32, 3),
        ('blk_type', c_uint32, 3),
        ('bad', c_uint32, 1),
        ('rsv0', c_uint32, 1),
        ('ecc_lvl', c_uint32, 4),
        ('repl_flag', c_uint32, 1),
        ('all_good', c_uint32, 1),
        ('xlc', c_uint32, 2),
        ('gc_class', c_uint32, 8),
        ('wf_flg', c_uint32, 1),
        ('rf_flg', c_uint32, 1),
        ('ecc_hi', c_uint32, 1),
        ('ecc_un', c_uint32, 1),
        ('dr_flg', c_uint32, 1),
        ('wl_flg', c_uint32, 1),
        ('rdist', c_uint32, 1),
        ('gc_soft', c_uint32, 1),
        ('nex_ptr', c_uint32, 16),
        ('mbu_cnt', c_uint32, 10),
        ('rsv1', c_uint32, 6),
        ('cr_tm', c_uint32),
        ('vpc', c_uint32),
        ('rd_cnt', c_uint32),
        ('seq_num', c_uint32),
        ('pe_cyc', c_uint32, 20),
        ('rsv2', c_uint32, 12),
        ('strem_id', c_uint32, 9),
        ('rsv3', c_uint32, 7),
        ('ext_lrb', c_uint32, 16),
        ('wfb0', c_uint32, 16),
        ('wfb1', c_uint32, 16),
        ('rfb0', c_uint32, 16),
        ('rfb1', c_uint32, 16),
        ('thr_cfg', c_uint32),
        ('rsv4', c_uint32),
        ('badb', c_uint16 * 32),
        ('rsv5', c_uint32),
        ('rsv6', c_uint64),
        ('rsv7', c_uint32, 16),
        ('hamming_ecc', c_uint32, 16),
    ]

class TahoeVUPower(Structure):
    """bmi format"""
    _pack_ = 1
    _fields_ = [
        ('vol', c_uint32, 16),
        ('cur', c_uint32, 16),
        ('max_credit', c_uint32),
        ('min_credit', c_uint32),
        ('avg_credit', c_uint32),
        ('max_rd_die', c_uint32),
        ('min_rd_die', c_uint32),
        ('avg_rd_die', c_uint32),
        ('max_wr_die', c_uint32),
        ('min_wr_die', c_uint32),
        ('avg_wr_die', c_uint32),
        ('max_ers_die', c_uint32),
        ('min_ers_die', c_uint32),
        ('avg_ers_die', c_uint32),
    ]
