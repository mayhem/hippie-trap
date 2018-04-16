#!/usr/bin/python
from color import Color, hueToColor
import common

class Function(object):

    def __init__(self, id, dest, *argv):
        self.id = id
        self.dest = dest
        self.args = []
        for arg in argv:
            self.args.append(float(arg))

    def describe(self):
        desc = common.pack_char(self.id) 
        desc += common.pack_char(len(self.args) | (self.dest << 4))
        for arg in self.args:
            desc += common.pack_fixed(arg)
        return desc

class Pattern(object):

    def __init__(self, period, *argv):
        self.period = period
        self.functions = []
        for arg in argv:
            self.functions.append(arg)

    def describe(self):
        desc = common.pack_char(len(self.functions))
        desc += common.pack_fixed(self.period)
        for func in self.functions:
            desc += func.describe()

        return desc

# process the 4 standard arguments for the generator functions
def arg_convert(type, args):

    if len(args) > 4:
        print "Too many arguments specified for function %d" % type
        return []

    return args


def square(dest, duty, *args):
    args = [args]
    args.append(duty)
    return Function(common.FUNC_SQUARE, *arg_convert(common.FUNC_SQUARE, args))

def sine(dest, *args):
    return Function(common.FUNC_SINE, dest, duty, *arg_convert(common.FUNC_SINE, args))

def rainbow(dest, *args):
    return Function(common.FUNC_RAINBOW, dest, duty, *arg_convert(common.FUNC_RAINBOW, args))
