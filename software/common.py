#!/usr/bin/python

import abc
from struct import pack

FUNC_NONE                  = 0
FUNC_SQUARE                = 1
FUNC_SINE                  = 2
FUNC_SAWTOOTH              = 3
FUNC_STEP                  = 4
FUNC_IMPULSE               = 5
FUNC_LINE                  = 6
FUNC_MAX                   = 6

MAX_NUM_ARGS           = 8
SCALE_FACTOR = 1000

def pack_char(ch):
    '''Pack a single character'''
    return bytearray(pack("<B", ch))

def pack_fixed(value):
    '''Convert value to a signed, scaled 4 byte integer'''
    return bytearray(pack("<i", int(value * SCALE_FACTOR)))

def pack_color(col):
    return bytearray(pack("<BBB", col[0], col[1], col[2]))

def dump(ba):
    for b in ba:
        print "%02X " % b,
    print
