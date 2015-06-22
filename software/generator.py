#!/usr/bin/python
import abc
import math
import random
import common

class GenOp(object):
    def __init__(self, operation, gen1, gen2):
        self.operation = operation
        self.g1 = gen1
        self.g2 = gen2

    def describe(self):
        desc = common.make_function(common.FUNC_GENOP, (common.ARG_FUNC,command.ARG_FUNC))
        desc += common.pack_fixed(self.operation)
        desc += self.g1.describe()
        desc += self.g2.describe()
        return desc + self.describe_next()

    def __getitem__(self, t):
        if self.operation == common.OP_ADD:
            return self.g1[t] + self.g2[t]
        elif self.operation == common.OP_SUB:
            return self.g1[t] - self.g2[t]
        elif self.operation == common.OP_MUL:
            return self.g1[t] * self.g2[t]
        elif self.operation == common.OP_SUB:
            return self.g1[t] * SCALE_FACTOR / self.g2[t]
        elif self.operation == common.OP_MOD:
            return self.g1[t] % self.g2[t]

        return 0.0

class Abs(object):

    def __init__(self, gen):
        self.g = gen

    def describe(self):
        desc = common.make_function(common.FUNC_ABS, (common.ARG_FUNC,))
        desc += self.g.describe()
        return desc

    def __getitem__(self, t):
        return abs(self.g[t])

class Constant(object):

    def __init__(self, value):
        self.value = value

    def describe(self):
        desc = common.make_function(common.FUNC_CONSTANT, (common.ARG_VALUE,))
        desc += common.pack_fixed(self.value)
        return desc

    def __getitem__(self, t):
        return self.value

class LocalRandomValue(object):

    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper
        self.value = lower + random.random() * (upper - lower)

    def describe(self):
        desc = common.make_function(common.FUNC_RANDOM, (common.ARG_VALUE,common.ARG_VALUE))
        desc += common.pack_fixed(self.lower)
        desc += common.pack_fixed(self.upper)
        return desc

    def __getitem__(self, t):
        return self.value

class Generator(object):

    def __init__(self, period, phase, amplitude, offset):
        self.period = period
        self.phase = phase
        self.amplitude = amplitude
        self.offset = offset

    @abc.abstractmethod
    def describe(self):
        pass

    @abc.abstractmethod
    def __getitem__(self, t):
        pass

class Sin(Generator):

    def __init__(self, period = 1.0, phase = 0.0, amplitude = 1.0, offset = .0):
        super(Sin, self).__init__(period, phase, amplitude, offset)

    def describe(self):
        desc = common.make_function(common.FUNC_SIN, (common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.phase)
        desc += common.pack_fixed(self.amplitude)
        desc += common.pack_fixed(self.offset)
        #print "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.period, self.phase, self.amplitude, self.offset),
        return desc

    def __getitem__(self, t):
        v = math.sin(t * self.period + self.phase) * self.amplitude + self.offset
        return v

class Square(Generator):

    def __init__(self, period = 1.0, phase = 0.0, amplitude = 1.0, offset = 0.0, duty=.5):
        super(Square, self).__init__(period, phase, amplitude, offset)
        if isinstance(self.period, object):
            self.period = self.period[0]
            print "local random period:", self.period
        self.duty = duty

    def describe(self):
        desc = common.make_function(common.FUNC_SQUARE, (common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.phase)
        desc += common.pack_fixed(self.amplitude)
        desc += common.pack_fixed(self.offset)
        desc += common.pack_fixed(self.duty)
        #print "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.period, self.phase, self.amplitude, self.offset),
        return desc

    def __getitem__(self, t):
        v = (t / self.period) + self.phase
        if float(v) % 1 >= self.duty:
            return self.amplitude + self.offset
        else:
            return self.offset

class Sawtooth(Generator):

    def __init__(self, period = 1.0, phase = 0.0, amplitude = 1.0, offset = 0.0):
        super(Sawtooth, self).__init__(period, phase, amplitude, offset)

    def describe(self):
        desc = common.make_function(common.FUNC_SAWTOOTH, (common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.phase)
        desc += common.pack_fixed(self.amplitude)
        desc += common.pack_fixed(self.offset)
        #print "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.period, self.phase, self.amplitude, self.offset),
        return desc

    def __getitem__(self, t):
        return (t * self.period + self.phase) % 1.0 * self.amplitude + self.offset

class Step(Generator):

    def __init__(self, period = 1.0, phase = 0.0, amplitude = 1.0, offset = 0.0):
        super(Step, self).__init__(period, phase, amplitude, offset)

    def describe(self):
        desc = common.make_function(common.FUNC_STEP, (common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.phase)
        desc += common.pack_fixed(self.amplitude)
        desc += common.pack_fixed(self.offset)
        #print "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.period, self.phase, self.amplitude, self.offset),
        return desc

    def __getitem__(self, t):
        v = (t / self.period) + self.phase
        if v > 0.0:
            return self.amplitude + self.offset
        else:
            return self.offset

class Sparkle(Generator):

    def __init__(self, period = 1.0, phase = 0.0, amplitude = 1.0, offset = 0.0):
        super(Sparkle, self).__init__(period, phase, amplitude, offset)

    def describe(self):
        desc = common.make_function(common.FUNC_SPARKLE, (common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.phase)
        desc += common.pack_fixed(self.amplitude)
        desc += common.pack_fixed(self.offset)
        #print "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, self.period, self.phase, self.amplitude, self.offset),
        return desc

    def __getitem__(self, t):
        v = (t / self.period) + self.phase
        if v < 1.0:
            return self.amplitude - t + self.offset
        if t >= 1.0:
            v = self.offset

class Line(Generator):

    def __init__(self, period = 1.0, phase = 0.0, amplitude = 1.0, offset = 0.0):
        super(Line, self).__init__(period, phase, amplitude, offset)

    def describe(self):
        desc = common.make_function(common.FUNC_LINE, (common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE, common.ARG_VALUE))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.phase)
        desc += common.pack_fixed(self.amplitude)
        desc += common.pack_fixed(self.offset)
        return desc

    def __getitem__(self, t):
        return (t * self.amplitude) + self.offset
