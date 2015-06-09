#!/usr/bin/python

import abc
from struct import pack

FUNC_FADE_IN           = 0
FUNC_FADE_OUT          = 1
FUNC_BRIGHTNESS        = 2
FUNC_SIN               = 3
FUNC_SQUARE            = 4
FUNC_SAWTOOTH          = 5
FUNC_CONSTANT_COLOR    = 6
FUNC_RAND_COL_SEQ      = 7
FUNC_HSV               = 8
FUNC_RAINBOW           = 9
FUNC_STEP              = 10

ARG_VALUE              = 0
ARG_FUNC               = 1
ARG_COLOR              = 2
ARG_CONSTANT           = 3

def make_function(id, args):
    flags = 0
    for i, arg in enumerate(args):
        flags |= arg << (i * 2);

    return bytearray(pack("<BH", (id << 4) | len(args), flags))

def pack_fixed(value):
    return bytearray(pack("<i", int(value * 1000)))

def pack_color(col):
    return bytearray(pack("<BBB", col[0], col[1], col[2]))

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
        #print "  ",
        if self.next:
            return self.next.describe()
        return bytearray([])
