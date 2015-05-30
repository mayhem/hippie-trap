#!/usr/bin/python
import abc
import math
import common

class Generator(object):

    def __init__(self, period, phase, offset, amplitude):
        self.period = period
        self.phase = phase
        self.offset = offset
        self.amplitude = amplitude

    @abc.abstractmethod
    def describe(self):
        pass

    @abc.abstractmethod
    def __getitem__(self, t):
        pass

class Sin(Generator):

    def __init__(self, period = 1.0, phase = 0.0, offset = .0, amplitude = 1):
        super(Sin, self).__init__(period, phase, offset, amplitude)

    def describe(self):
        desc = common.make_function(common.FUNC_SIN, (common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.phase)
        desc += common.pack_fixed(self.offset)
        desc += common.pack_fixed(self.amplitude)
        print "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.period, self.phase, self.offset, self.amplitude),
        return desc

    def __getitem__(self, t):
        v = math.sin(t * self.period + self.phase) * self.amplitude + self.offset
        return v

# TODO: Review implementation
class Square(Generator):

    def __init__(self, period = 1.0, phase = 0.0, offset = 0.0, amplitude = 1.0):
        super(Square, self).__init__(period, phase, offset, amplitude)

    def describe(self):
        desc = common.make_function(common.FUNC_SQUARE, (common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.phase)
        desc += common.pack_fixed(self.offset)
        desc += common.pack_fixed(self.amplitude)
        print "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.period, self.phase, self.offset, self.amplitude),
        return desc

    def __getitem__(self, t):
        v = (t / self.period) + self.phase
        if float(v) % 1 >= .5:
            return self.amplitude + self.offset
        else:
            return self.offset

class Sawtooth(Generator):

    def __init__(self, period = 1.0, phase = 0.0, offset = 0.0, amplitude = 1.0):
        super(Sawtooth, self).__init__(period, phase, offset, amplitude)

    def describe(self):
        desc = common.make_function(common.FUNC_SAWTOOTH, (common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.phase)
        desc += common.pack_fixed(self.offset)
        desc += common.pack_fixed(self.amplitude)
        print "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.period, self.phase, self.offset, self.amplitude),
        return desc

    def __getitem__(self, t):
        return (t * self.period + self.phase) % 1.0 * self.amplitude + self.offset
