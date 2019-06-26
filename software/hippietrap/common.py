#!/usr/bin/python

import abc
from struct import pack

FUNC_NONE                  = 0
FUNC_ERROR                 = 1
FUNC_SQUARE                = 2
FUNC_SINE                  = 3
FUNC_SAWTOOTH              = 4
FUNC_STEP                  = 5
FUNC_LINE                  = 6
FUNC_IMPULSE               = 7
FUNC_RAINBOW               = 8
FUNC_MAX                   = FUNC_IMPULSE

DEST_LED_0        =  0
DEST_LED_1        =  1
DEST_LED_2        =  2
DEST_LED_3        =  3
DEST_LED_4        =  4
DEST_LED_5        =  5
DEST_LED_6        =  6
DEST_LED_7        =  7
DEST_LED_8        =  8
DEST_LED_9        =  9
DEST_LED_10       = 10
DEST_LED_11       = 10
DEST_ALL          = 12
DEST_ALL_RED      = 13
DEST_ALL_BLUE     = 14
DEST_ALL_GREEN    = 15

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
