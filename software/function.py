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
