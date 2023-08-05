#!/usr/bin/env python
# pylint: disable=attribute-defined-outside-init,
"""
Created on 2020/06/06

@author: yyang
"""
import re
from ctypes import Structure, c_uint8, c_uint64, Union, string_at, addressof, sizeof, Array

from utils import log


class Uint128(Structure):
    _pack_ = 1
    _fields_ = [
        ('LOW', c_uint64),
        ('HIGH', c_uint64),
    ]

    def __init__(self, value=0, **kwargs):
        super(Uint128, self).__init__(**kwargs)
        self.value = value

    def __str__(self):
        return str(self.value)

    def _get_(self):
        return (self.HIGH << 64) | self.LOW

    def _set_(self, value):
        self.HIGH = value >> 64
        self.LOW = value & ((1 << 64) - 1)

    def _del_(self):
        self.LOW = 0
        self.HIGH = 0

    value = property(_get_, _set_, _del_, 'value operation')


class Byte(Structure):
    _pack_ = 1
    _fields_ = [
        ('BYTE', c_uint8),
    ]


class Ctype(object):
    def __init__(self, ctype, name='NAME'):
        self._name = name
        self._ctype = ctype
        self._lines = list()

    @staticmethod
    def _format(indent, name, index=None):
        if index is None:
            return '{}{}'.format(' ' * indent, name)
        return '{}{} [{}]'.format(' ' * indent, name, index)

    @staticmethod
    def _desc(ctype, name):
        try:
            name = getattr(ctype, 'desc').get(name, name)
        except:
            pass
        return name

    def _parser(self, ctype, skip, indent=0, name=''):
        if isinstance(type(ctype), (type(Union), type(Structure))):
            if isinstance(ctype, Uint128):
                self._lines.append([self._format(indent, self._desc(ctype, name)), ctype.value])
                return

            for field in getattr(ctype, '_fields_'):
                name = field[0]
                if [i for i in skip if i in name]:
                    continue
                _ctype = getattr(ctype, name)

                self._parser(_ctype, skip, indent, self._desc(ctype, name))
        elif isinstance(type(ctype), (type(Array), )):
            if isinstance(ctype[0], Byte):
                string = string_at(addressof(ctype), sizeof(ctype)).decode('utf-8', errors='ignore')
                string = re.sub(r'[\x00-\x1f]', '', string).strip()
                if string:
                    self._lines.append([self._format(indent, name), string])
            elif isinstance(type(ctype[0]), (type(Union), type(Structure))):
                for i, value in enumerate(ctype):
                    self._lines.append([self._format(indent, name, i), ' '])
                    self._parser(value, skip, indent + 2)
            else:
                for i, value in enumerate(ctype):
                    self._lines.append([self._format(indent, name, i), value])
        else:
            self._lines.append([self._format(indent, name), ctype])

    def write(self, path, mode='wb'):
        with open(path, mode) as fd:
            fd.write(self._ctype)

    def get(self, name):
        ctype = getattr(self._ctype, name)
        if isinstance(ctype, Uint128):
            return ctype.value
        elif isinstance(type(ctype), type(Array)):
            if isinstance(ctype[0], Byte):
                string = string_at(addressof(ctype), sizeof(ctype)).decode('utf-8', errors='ignore')
                return re.sub(r'[\x00-\x1f]', '', string).strip()
        return ctype

    def dump(self, skip=None, no_rsv=True, only_values=False):
        self._lines = list()
        skip = skip if skip else list()
        if no_rsv:
            skip += ['rsv', 'RSV']
        none_list = (0x0, '', None)

        self._parser(self._ctype, skip)

        name_list = [len(n) for n, v in self._lines if not only_values or v not in none_list] + [len(self._name)]
        max_name_len = max(name_list)
        f_title = '| {{:<{}}} | {{:<34}} | {{:<39}} |'.format(max_name_len)
        f_name = '{{:<{}}}'.format(max_name_len)

        log.DUMP(f_title.format(self._name, 'HEX', 'DEC'))
        log.DUMP('-' * (83 + max_name_len))
        for name, value in self._lines:
            if only_values and value in none_list:
                continue

            line = list()
            line.append(f_name.format(name))
            if isinstance(value, (bool, int, float)):
                line.append("{:<#34x}".format(value))
                line.append("{:<39}".format(value))
            else:
                line.append("{:76}".format(value))

            log.DUMP("| {} |".format(" | ".join(line)))
        log.DUMP('-' * (83 + max_name_len))
