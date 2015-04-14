#!/usr/bin/python
import abc
import math

# Generator -> Sawtooth, Sine, Cos, Square, Hilbert, Impulse
# ColorSource -> given t: get color
# Filter -> given t, color: return color

#Generator(args)
#ColorSource(Generator, args)
#Filter(Time

#rainbow = HSVtoRGB(Sawtooth(), 1.0, 1.0)

class Generator(object):

    def __init__(self, period, phase):
        self.period = period
        self.phase = phase

    @abc.abstractmethod
    def __getitem__(self, t):
        pass

class Sin(Generator):

    def __init__(self, period, phase):
        super(Sin, self).__init__(period, phase)

    def __getitem__(self, t):
        return math.sin(t * self.period) + self.phase

class Cos(Generator):

    def __init__(self, period, phase):
        super(Cos, self).__init__(period, phase)

    def __getitem__(self, t):
        return math.cos(t * self.period) + self.phase

class Square(Generator):

    def __init__(self, period, phase):
        super(Square, self).__init__(period, phase)

    def __getitem__(self, t):
        v = (t * self.period) + self.phase
        if float(t) % 1 >= .5:
            return 1.0
        else:
            return 0.0

class Sawtooth(Generator):

    def __init__(self, period, phase):
        super(Sawtooth, self).__init__(period, phase)

    def __getitem__(self, t):
        return (t * self.period + self.phase) % 1.0

class Triangle(Generator):

    def __init__(self, period, phase):
        super(Triangle, self).__init__(period, phase)

    def __getitem__(self, t):
        return math.fabs(t % (self.period * 2) - self.period) + self.phase


