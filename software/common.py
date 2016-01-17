#!/usr/bin/python

import abc
from struct import pack

FUNC_FADE_IN               = 0
FUNC_FADE_OUT              = 1
FUNC_BRIGHTNESS            = 2
FUNC_SIN                   = 3
FUNC_SQUARE                = 4
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

ARG_VALUE              = 0
ARG_FUNC               = 1
ARG_COLOR              = 2
ARG_SRC                = 3

MAX_NUM_ARGS           = 8

OP_ADD = 0
OP_SUB = 1
OP_MUL = 2
OP_DIV = 3
OP_MOD = 4

SCALE_FACTOR = 1000


def make_function(id, args):
    flags = 0
    for i, arg in enumerate(args):
        flags |= arg << (i * 2);

    if len(args) > 8:
        raise ValueError("Functions cannot have more than 8 arguments")

    if id > FUNC_MAX:
        raise ValueError("Max 32 functions are allowed.")

    return bytearray(pack("<BH", (id << 3) | len(args), flags))

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

class ChainLink(object):

    def __init__(self):
        self.next = None

    @abc.abstractmethod
    def describe(self):
        pass

    def chain(self, next):
        if not self.next:
            self.next = next
        else:
            self.next.chain(next)

    def call_next(self, t, col):
        if self.next:
            return self.next.filter(t, col)
        return col 

    def describe_next(self):
        if self.next:
            return self.next.describe()
        return bytearray([])

    def get_filter_count(self):
        count = 0
        filter = self.next
        while filter:
            count += 1
            filter = filter.next

        return count
