#!/usr/bin/python

import abc
from struct import pack

FUNC_NONE                  = 0
FUNC_SQUARE                = 1

FUNC_SAWTOOTH              = 5
FUNC_CONSTANT_COLOR        = 6
FUNC_RAND_COL_SEQ          = 7
FUNC_HSV                   = 8
FUNC_RAINBOW               = 9
FUNC_STEP                  = 10
FUNC_SPARKLE               = 11
FUNC_GENOP                 = 12
FUNC_SRCOP                 = 13
FUNC_ABS                   = 14
FUNC_LINE                  = 15
FUNC_CONSTANT              = 16
FUNC_COMPLEMENTARY         = 17
FUNC_LOCAL_RANDOM          = 18
FUNC_IMPULSE               = 19
FUNC_REPEAT_LOCAL_RANDOM   = 20
FUNC_CONSTANT_RANDOM_COLOR = 21
FUNC_COLOR_SHIFT           = 22
FUNC_RGB_SRC               = 23
FUNC_XYZ_SRC               = 24
FUNC_LOCAL_ANGLE           = 25

FUNC_MAX               = 31

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
