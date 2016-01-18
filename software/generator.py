#!/usr/bin/python
import abc
import math
import random
import common

def plot(g):
    import matplotlib.pyplot as plt
    t = -2.0
    end = 2.0
    step = .01

    x = []
    y = []
    while t <= end:
        x.append(t)
        y.append(g[t])
        t += step

    plt.plot(x, y)
    plt.ylabel('value')
    plt.xlabel('time')
    plt.show()

MAX_LOCAL_RANDOM_VALUES = 6
local_random_values = []

def clear_local_random_values():
    global local_random_values
    local_random_values = []

def set_local_random_value(value):
    global local_random_values
#    if len(local_random_values) >= MAX_LOCAL_RANDOM_VALUES:
#        print "Warning: attempting to store more than %d random values -- it won't be repeatable." % MAX_LOCAL_RANDOM_VALUES
    local_random_values.append(value)

def get_local_random_value(index):
    global local_random_values
    if len(local_random_values) <= index:
        raise KeyError("Invalid get local random index: %d" % index)
    return local_random_values[index]

class GeneratorBase(object):
    pass

class GenOp(GeneratorBase):
    def __init__(self, operation, gen1, gen2):
        if not isinstance(gen1, GeneratorBase) or not isinstance(gen2, GeneratorBase):
            raise TypeError("GenOp needs to be passed two Generator objects")
        self.operation = operation
        self.g1 = gen1
        self.g2 = gen2

    def describe(self):
        desc = common.make_function(common.FUNC_GENOP, (common.ARG_VALUE, common.ARG_FUNC,common.ARG_FUNC))
        desc += common.pack_fixed(self.operation)
        desc += self.g1.describe()
        desc += self.g2.describe()
        return desc + self.describe_next()

    def describe_next(self):
        return bytearray([])

    def __getitem__(self, t):
        if self.operation == common.OP_ADD:
            return self.g1[t] + self.g2[t]
        elif self.operation == common.OP_SUB:
            return self.g1[t] - self.g2[t]
        elif self.operation == common.OP_MUL:
            return self.g1[t] * self.g2[t]
        elif self.operation == common.OP_SUB:
            return self.g1[t] / self.g2[t]
        elif self.operation == common.OP_MOD:
            return self.g1[t] % self.g2[t]

        return 0.0

class Abs(GeneratorBase):

    def __init__(self, gen):
        self.g = gen

    def describe(self):
        desc = common.make_function(common.FUNC_ABS, (common.ARG_FUNC,))
        desc += self.g.describe()
        return desc

    def __getitem__(self, t):
        return abs(self.g[t])

class Constant(GeneratorBase):

    def __init__(self, value):
        self.value = value

    def describe(self):
        desc = common.make_function(common.FUNC_CONSTANT, (common.ARG_VALUE,))
        desc += common.pack_fixed(self.value)
        return desc

    def __getitem__(self, t):
        return self.value

class LocalAngle(GeneratorBase):

    def describe(self):
        return common.make_function(common.FUNC_LOCAL_ANGLE, ())

    def __getitem__(self, t):
        return 0

class LocalRandomValue(GeneratorBase):

    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper
        self.value = lower + random.random() * (upper - lower)
        set_local_random_value(self.value)

    def describe(self):
        desc = common.make_function(common.FUNC_LOCAL_RANDOM, (common.ARG_VALUE,common.ARG_VALUE))
        desc += common.pack_fixed(self.lower)
        desc += common.pack_fixed(self.upper)
        return desc

    def __getitem__(self, t):
        return self.value

class RepeatLocalRandomValue(GeneratorBase):

    def __init__(self, index):
        self.index = index
        self.value = get_local_random_value(index)

    def describe(self):
        desc = common.make_function(common.FUNC_REPEAT_LOCAL_RANDOM, (common.ARG_VALUE,))
        desc += common.pack_fixed(self.index)
        return desc

    def __getitem__(self, t):
        return self.value

class Generator(GeneratorBase):

    def __init__(self, period, phase, amplitude, offset):
        self.period = period
        self.phase = phase
        self.amplitude = amplitude
        self.offset = offset

        if type(self.period) in (int, float):
            self.period_f = None
        else:
            self.period_f = self.period
            self.period = self.period_f[0]

        if self.period == 0.0:
            raise ValueError("Period 0 is invalid")

        if type(self.phase) in (int, float):
            self.phase_f = None
        else:
            self.phase_f = self.phase
            self.phase = self.phase_f[0]

        if type(self.amplitude) in (int, float):
            self.amplitude_f = None
        else:
            self.amplitude_f = self.amplitude
            self.amplitude = self.amplitude_f[0]

        if type(self.offset) in (int, float):
            self.offset_f = None
        else:
            self.offset_f = self.offset
            self.offset = self.offset_f[0]

    @abc.abstractmethod
    def describe(self):
        pass

    def _describe(self):
        args = []
        desc = bytearray()

        if self.period_f:
            desc += self.period_f.describe()
            args.append(common.ARG_FUNC)
        else:
            desc += common.pack_fixed(self.period)
            args.append(common.ARG_VALUE)

        if self.phase_f:
            desc += self.phase_f.describe()
            args.append(common.ARG_FUNC)
        else:
            desc += common.pack_fixed(self.phase)
            args.append(common.ARG_VALUE)

        if self.amplitude_f:
            desc += self.amplitude_f.describe()
            args.append(common.ARG_FUNC)
        else:
            desc += common.pack_fixed(self.amplitude)
            args.append(common.ARG_VALUE)

        if self.offset_f:
            desc += self.offset_f.describe()
            args.append(common.ARG_FUNC)
        else:
            desc += common.pack_fixed(self.offset)
            args.append(common.ARG_VALUE)

        return (desc, args)

    @abc.abstractmethod
    def __getitem__(self, t):
        pass


class Sin(Generator):

    def __init__(self, period = 1.0, phase = 0, amplitude = .5, offset = .5):
        # convert from using pesky pi to using parametric values
        super(Sin, self).__init__(period, phase, amplitude, offset)

    def describe(self):
        desc, args = self._describe()
        return common.make_function(common.FUNC_SIN, args) + desc

    def __getitem__(self, t):
        period = math.pi / (self.period/2.0)
        phase = (-math.pi / 2.0) + (math.pi * 2 * self.phase)
        v = math.sin(t * period + phase) * self.amplitude + self.offset
        return v

class Square(Generator):

    def __init__(self, period = 1.0, phase = 0.0, amplitude = 1.0, offset = 0.0, duty=.5):
        super(Square, self).__init__(period, phase, amplitude, offset)
        self.duty = duty
        if type(self.duty) in (int, float):
            self.duty_f = None
        else:
            self.duty_f = self.duty
            self.duty = self.duty_f[0]

    def describe(self):
        desc, args = self._describe()

        if self.duty_f: 
            desc += self.duty_f.describe()
            args.append(common.ARG_FUNC)
        else:
            desc += common.pack_fixed(self.duty)
            args.append(common.ARG_VALUE)

        return common.make_function(common.FUNC_SQUARE, args) + desc

    def __getitem__(self, t):
        v = (t / self.period) + self.phase
        if float(v) % 1 < self.duty:
            return self.amplitude + self.offset
        else:
            return self.offset

class Sawtooth(Generator):

    def __init__(self, period = 1.0, phase = 0.0, amplitude = 1.0, offset = 0.0):
        super(Sawtooth, self).__init__(period, phase, amplitude, offset)

    def describe(self):
        desc, args = self._describe()
        return common.make_function(common.FUNC_SAWTOOTH, args) + desc

    def __getitem__(self, t):
        period = 1.0 / self.period
        return (t * period + self.phase) % 1.0 * self.amplitude + self.offset

class Step(Generator):

    def __init__(self, period = 1.0, phase = 0.0, amplitude = 1.0, offset = 0.0):
        super(Step, self).__init__(period, phase, amplitude, offset)

    def describe(self):
        desc, args = self._describe()
        return common.make_function(common.FUNC_STEP, args) + desc

    def __getitem__(self, t):
        v = (t / self.period) + self.phase
        if v >= 0.0:
            return self.amplitude + self.offset
        else:
            return self.offset

class Impulse(Generator):

    def __init__(self, period = 1.0, phase = 0.0, amplitude = 1.0, offset = 0.0):
        super(Impulse, self).__init__(period, phase, amplitude, offset)

    def describe(self):
        desc, args = self._describe()
        return common.make_function(common.FUNC_IMPULSE, args) + desc

    def __getitem__(self, t):
        v = (t / self.period) + self.phase
        if v >= 0.0 and v < 1.0:
            return self.amplitude + self.offset
        else:
            return self.offset

class Sparkle(Generator):

    def __init__(self, period = 1.0, phase = 0.0, amplitude = 1.0, offset = 0.0):
        super(Sparkle, self).__init__(period, phase, amplitude, offset)

    def describe(self):
        desc, args = self._describe()
        return common.make_function(common.FUNC_SPARKLE, args) + desc

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
        desc, args = self._describe()
        return common.make_function(common.FUNC_LINE, args) + desc

    def __getitem__(self, t):
        return (t * self.amplitude) + self.offset
