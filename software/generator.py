#!/usr/bin/python
import abc
import math

class Generator(object):

    def __init__(self, period, phase, offset, amplitude):
        self.period = period
        self.phase = phase
        self.offset = offset
        self.amplitude = amplitude

    @abc.abstractmethod
    def describe(self, level = 0):
        pass

    @abc.abstractmethod
    def __getitem__(self, t):
        pass

class Sin(Generator):

    def __init__(self, period = 1.0, phase = 0.0, offset = .0, amplitude = .0):
        super(Sin, self).__init__(period, phase, offset, amplitude)

    def describe(self, level = 0):
        print "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.period, self.phase, self.offset, self.amplitude),

    def __getitem__(self, t):
        v = math.sin(t * self.period + self.phase) * self.amplitude + self.offset
        return v

# TODO: Review implementation
class Square(Generator):

    def __init__(self, period = 1.0, phase = 0.0, offset = 0.0, amplitude = 1.0):
        super(Square, self).__init__(period, phase, offset, amplitude)

    def describe(self, level = 0):
        print "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.period, self.phase, self.offset, self.amplitude),

    def __getitem__(self, t):
        v = (t / self.period) + self.phase
        if float(v) % 1 >= .5:
            return self.amplitude + self.offset
        else:
            return self.offset

class Sawtooth(Generator):

    def __init__(self, period = 1.0, phase = 0.0, offset = 0.0, amplitude = 1.0):
        super(Sawtooth, self).__init__(period, phase, offset, amplitude)

    def describe(self, level = 0):
        print "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.period, self.phase, self.offset, self.amplitude),

    def __getitem__(self, t):
        return (t * self.period + self.phase) % 1.0 + self.offset

# TODO: Review implementation
#class Triangle(Generator):
#
#    def __init__(self, period = 1.0, phase = 0.0, offset = 0.0):
#        super(Triangle, self).__init__(period, phase, offset)
#
#    def __getitem__(self, t):
#        return math.fabs(t % (self.period * 2) - self.period) + self.phase
