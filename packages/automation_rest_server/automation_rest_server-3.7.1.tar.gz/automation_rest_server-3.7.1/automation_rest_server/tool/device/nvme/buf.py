#!/usr/bin/env python
"""
Created on 2017/3/3

@author: yyang
"""
import os
import platform
import re
import random
from ctypes import POINTER, cast, sizeof, addressof, memmove, memset, pointer
from ctypes import c_uint8, c_uint16, c_uint32, c_uint64, string_at, CDLL, c_void_p

from tool.device.nvme.ctype import Ctype
from utils import log


class NVMeMalloc(object):
    def __init__(self, length=4096):
        filename = 'buf.dll' if platform.system() == 'Windows' else 'buf.so'
        path = os.path.realpath(os.path.join(os.getcwd(), "lib", "driver", "dll", filename))
        self._dll = CDLL(path)
        self._dll.nvme_alloc.restype = c_uint64

        self._ptr = self._dll.nvme_alloc(length)
        assert self._ptr != 0, 'Malloc {:#x} Failed!'.format(length)

    def __del__(self):
        self.free()

    def mem_copy(self, dptr, size):
        self._dll.nvme_copy(self.ptr, dptr, size)

    def free(self):
        if self._ptr:
            self._dll.nvme_free(self.ptr)

    @property
    def ptr(self):
        return c_void_p(self._ptr)

    @property
    def address(self):
        return self._ptr


# noinspection PyTypeChecker
class Malloc(object):
    def __init__(self, length=1, types=c_uint8):
        filename = 'buf.dll' if platform.system() == 'Windows' else 'buf.so'
        path = os.path.realpath(os.path.join(os.getcwd(), "lib", "driver", "dll", filename))
        self.m_dll = CDLL(path)

        self._types = types  # types of item
        self._len = length  # count of items
        self._sizeof = sizeof(self._types)  # size of item
        self._size = self._len * self._sizeof  # count of bytes
        # noinspection PyTypeChecker,PyCallingNonCallable
        self._buf = (self._types * self._len)()  # buffer instance

        self._lp_uint8 = cast(self._buf, POINTER(c_uint8))
        self._lp_uint16 = cast(self._buf, POINTER(c_uint16))
        self._lp_uint32 = cast(self._buf, POINTER(c_uint32))
        self._lp_uint64 = cast(self._buf, POINTER(c_uint64))

    def __getitem__(self, key):
        return self._buf[key]

    def __setitem__(self, key, val):
        self._buf[key] = val

    def realloc(self, types=c_uint8):
        assert self._size % sizeof(types) == 0, 'Buffer is unaligned as type of {}'.format(types)

        self._types = types
        self._sizeof = sizeof(self._types)
        self._len = self._size // self._sizeof
        _buf = (self._types * self._len)()
        memmove(_buf, self._buf, self._size)
        self._buf = _buf

        self._lp_uint8 = cast(self._buf, POINTER(c_uint8))
        self._lp_uint16 = cast(self._buf, POINTER(c_uint16))
        self._lp_uint32 = cast(self._buf, POINTER(c_uint32))
        self._lp_uint64 = cast(self._buf, POINTER(c_uint64))

    @property
    def len(self):
        return self._len

    @property
    def size(self):
        return self._size

    @property
    def sizeof(self):
        return self._sizeof

    @property
    def types(self):
        return self._types

    @property
    def buf(self):
        return self._buf

    @property
    def address(self):
        return addressof(self._buf)

    @property
    def pointer(self):
        return pointer(self._buf)

    def cast(self, types):
        return cast(self._buf, POINTER(types))

    def convert(self, types, index=0):
        return cast(self._buf, POINTER(types))[index]

    def memset(self, byte):
        memset(self._buf, byte, self.size)

    def memmove(self, offset, source, start, length):
        memmove(self.address + offset, source.address + start, length)

    def memcopy(self, stream, offset=0, length=0):
        data = [ord(i) for i in list(stream)]
        size = min(length, len(data), self.size) if length > 0 else min(len(data), self.size)
        for i in range(size):
            self.set_uint8(offset + i, data[i])

    def get_uint8(self, offset):
        return self._lp_uint8[offset]

    def get_uint16(self, offset):
        return self._lp_uint16[offset // 2]

    def get_uint32(self, offset):
        return self._lp_uint32[offset // 4]

    def get_uint64(self, offset):
        return self._lp_uint64[offset // 8]

    def set_uint8(self, offset, value):
        self._lp_uint8[offset] = value

    def set_uint16(self, offset, value):
        self._lp_uint16[offset // 2] = value

    def set_uint32(self, offset, value):
        self._lp_uint32[offset // 4] = value

    def set_uint64(self, offset, value):
        self._lp_uint64[offset // 8] = value

    def translate(self, start, size=0, types=c_uint8):
        _sizeof = sizeof(types)

        assert start >= 0 and size >= 0, 'Start: {:#x} or Size: {:#x} < 0!'.format(start, size)
        assert start + size <= self.size, 'Start: {:#x} + Size: {:#x} > Max: {:#x}!'.format(start, size, self.size)
        assert start % _sizeof == 0, 'Start: {:#x} is not aligned with type: {}!'.format(start, types)
        assert size % _sizeof == 0, 'Size: {:#x} is not aligned with type: {}!'.format(size, types)

        length = size // _sizeof if size > 0 else (self.size - start) // _sizeof
        offset = start // _sizeof
        return cast(self._buf, POINTER(types)), offset, length

    def fill_uint32_seq(self, value=0, start=0, size=0, step=1):
        self.m_dll.fill_uint32_seq(*self.translate(start, size, c_uint32), value, step)

    def fill_uint32_fix(self, value=0, start=0, size=0):
        self.m_dll.fill_uint32_fix(*self.translate(start, size, c_uint32), value)

    def fill_uint32_rnd(self, seed=0, start=0, size=0):
        self.m_dll.fill_uint32_rnd(*self.translate(start, size, c_uint32), seed)

    def compare_uint32_seq(self, value=0, start=0, size=0, step=1):
        return self.m_dll.compare_uint32_seq(*self.translate(start, size, c_uint32), value, step)

    def compare_uint32_fix(self, value=0, start=0, size=0):
        return self.m_dll.compare_uint32_fix(*self.translate(start, size, c_uint32), value)

    def compare_uint32_rnd(self, seed=0, start=0, size=0):
        return self.m_dll.compare_uint32_rnd(*self.translate(start, size, c_uint32), seed)

    def diff_uint32_seq(self, value=0, start=0, size=0):
        buffer, offset, length = self.translate(start, size, c_uint32)
        log.DUMP("  Address  :  Expected   Actual")
        log.DUMP("-----------------------------------")
        for i in range(offset, offset + length):
            if buffer[i] != value + i:
                log.DUMP("{:#010x} : {:#010x} {:#010x}".format(i * 4, value + i, buffer[i]))
        log.DUMP("-----------------------------------")

    def diff_uint32_fix(self, value=0, start=0, size=0):
        buffer, offset, length = self.translate(start, size, c_uint32)
        log.DUMP("  Address  :  Expected   Actual")
        log.DUMP("-----------------------------------")
        for i in range(offset, offset + length):
            if buffer[i] != value:
                log.DUMP("{:#010x} : {:#010x} {:#010x}".format(i * 4, value, buffer[i]))
        log.DUMP("-----------------------------------")

    def diff_uint32_rnd(self, seed=0, start=0, size=0):
        _random = random.Random(seed)
        buffer, offset, length = self.translate(start, size, c_uint32)
        log.DUMP("  Address  :  Expected   Actual")
        log.DUMP("-----------------------------------")
        for i in range(offset, offset + length):
            excepted = _random.randrange(0, 1 << 32)
            if buffer[i] != excepted:
                log.DUMP("{:#010x} : {:#010x} {:#010x}".format(i * 4, excepted, buffer[i]))
        log.DUMP("-----------------------------------")

    def fill_uint8_fix(self, value=0, start=0, size=0):
        self.m_dll.fill_uint8_fix(*self.translate(start, size, c_uint8), value)

    def look_idx_uint32(self, value):
        return self.m_dll.look_idx_uint32(self.buf, self.size // 4, value)

    def compare(self, dst, src_start=0, src_size=0, dst_start=None, dst_size=None):
        dst_start = src_start if dst_start is None else dst_start
        dst_size = src_size if dst_size is None else dst_size
        src_size = min(src_size, self.size - src_start) if src_size > 0 else self.size - src_start
        dst_size = min(dst_size, dst.size - dst_start) if dst_size > 0 else dst.size - dst_start

        return self.m_dll.compare(self.buf, dst.buf, src_start, dst_start, min(src_size, dst_size))

    def dump(self, skip=None, no_rsv=True, only_values=False):
        Ctype(self._buf).dump(skip=skip, no_rsv=no_rsv, only_values=only_values)

    def dump_diff(self, dst, src_start=0, src_size=0, dst_start=None, dst_size=None):
        dst_start = dst_start if dst_start is not None else src_start
        dst_size = dst_size if dst_size is not None else src_size

        src_buf, src_off, src_len = self.translate(src_start, src_size, c_uint32)
        dst_buf, dst_off, dst_len = dst.translate(dst_start, dst_size, c_uint32)
        log.DUMP("")

        log.DUMP("  ADDR_A  /  ADDR_B   :   DATA_A     DATA_B")
        log.DUMP("---------------------------------------------")
        for i in range(min(src_len, dst_len)):
            src_index = i + src_off
            dst_index = i + dst_off
            if src_buf[src_index] != dst_buf[dst_index]:
                log.DUMP("{:#010x}/{:#010x} : {:#010x} {:#010x}".format(
                    src_index * 4, dst_index * 4, src_buf[src_index], dst_buf[dst_index]))

    def dump_uint8(self, start=0, size=0):
        log.DUMP("          0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f")
        log.DUMP("---------------------------------------------------------")

        buffer, offset, length = self.translate(start, size, c_uint8)

        for i in range(offset, offset + length, 0x10):
            data = ["{:02x}".format(d) for d in buffer[i:min(i + 0x10, offset + length)]]
            log.DUMP("{:#08x}: {}".format(i, " ".join(data)))

    def dump_uint32(self, start=0, size=0):
        log.DUMP("         0        1        2        3       ")
        log.DUMP("--------------------------------------------")

        buffer, offset, length = self.translate(start, size, c_uint32)

        for i in range(offset, offset + length, 0x4):
            data = ["{:08x}".format(d) for d in buffer[i:min(i + 0x4, offset + length)]]
            log.DUMP("{:#08x}: {}".format(i * 4, " ".join(data)))

    def dump_uint8_uart(self, start=0, size=0):
        buffer, offset, length = self.translate(start, size, c_uint8)

        for i in range(offset, offset + length, 0x10):
            data = ["{:02x}".format(d) for d in buffer[i:min(i + 0x10, offset + length)]]
            log.DUMP("{}".format(" ".join(data)))

    def set_sub_buffer(self, offset, size, types=c_uint8):
        p_buff = cast(self._buf, POINTER(c_uint8))
        d_list = Malloc(size//sizeof(types), types)
        if (offset + size) > self._len:
            raise RuntimeError("[ERR] out of range(offset: {}, size: {})".format(offset, size))
        for off in range(offset, offset + size):
            d_list.set_uint8(off - offset, p_buff[off])
        return d_list

    def mask(self, buff):
        for i in range(buff.size):
            mask = buff.get_uint8(i)
            if mask == 1:
                self.set_uint8(i, 0)

    def get_string(self, offset, length):
        dat_list = list()
        p_buff = cast(self._buf, POINTER(c_uint8))
        for i in range(length):
            off = offset + i
            ret = "{:#04x}".format(p_buff[off])
            dat_list.append(ret)
        dat_list.reverse()
        ret = "".join(dat_list)
        return ret

    @staticmethod
    def to_number(array):
        string = '{{:0{}x}}'.format(sizeof(array) // len(array) * 2)
        data = [string.format(i) for i in array]
        return int(''.join(data), 16)

    @staticmethod
    def to_string(ctype, length=0):
        length = length if length else sizeof(ctype)
        string = string_at(addressof(ctype), length).decode('utf-8', errors='ignore')
        return re.sub(r'[\x00-\x1f]', '', string).strip()

    def set_multi_bytes(self, offset, length, buff):
        for i in range(length):
            self.set_uint8(offset + i, buff.get_uint8(i))

    def set_multi_bytes_fix(self, offset, length, val):
        for i in range(length):
            self.set_uint8(offset + i, val)

    def set_multi_dword(self, stream, offset=0, length=1):
        for i in range(length):
            self.set_uint32(offset + i * 4, stream[i])

    def set_multi_qword(self, stream, offset=0, length=1):
        for i in range(length):
            self.set_uint64(offset + i * 8, stream[i])

    def write(self, path, mode='wb'):
        with open(path, mode) as fd:
            fd.write(self._buf)

    def read(self, path):
        with open(path, "rb") as fd:
            memmove(self._buf, fd.read(), self._size)

    def write_string(self, path, mode='wb'):
        with open(path, mode) as fd:
            string = "".join([chr(i) for i in cast(self._buf, POINTER(c_uint8))])
            fd.write(string)


def generate_big_number(array):
    """
    Generate as a big number with data of array
    :param array: Ctypes array
    :return:      Unsigned number
    """
    total = 0
    bits = sizeof(type(array)) // len(array) * 8
    for i, num in enumerate(array):
        total += (num << (i * bits))
    return total


def get_string(array, little_endian=True):
    """
    Generate as a hex number with data of array
    :param array:           Ctypes array
    :param little_endian:   Little endian or big endian
    :return:                String of hex number without 0x
    """
    content_list = ["{:02x}".format(x) for x in array]
    if little_endian:
        content_list.reverse()
    return "".join(content_list)
