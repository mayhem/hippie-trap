#!/usr/bin/python
import abc
import math
import colorsys
import generator
import random
from color import Color, hueToColor
from common import ChainLink

class ColorSource(ChainLink):

    def __init__(self, generator):
        super(ColorSource, self).__init__()
        self.g = generator
        self.next = None

    def describe(self, level = 0):
        print "%s(" % self.__class__.__name__,
        if self.g:
            self.g.describe(level+1)
        print ")",

    @abc.abstractmethod
    def __getitem__(self, t):
        pass

class ConstantColor(ColorSource):

    def __init__(self, color):
        self.color = color
        super(ConstantColor, self).__init__(None)

    def describe(self, level = 0):
        print "%s()" % (self.__class__.__name__)
        self.describe_next()

    def __getitem__(self, t):
        return self.call_next(t, self.color)

class RandomColorSequence(ColorSource):
    '''
       Return colors that appear _random_ to a human.
    '''

    def __init__(self, period, seed=0):
        self.period = period
        self.seed = seed
        super(RandomColorSequence, self).__init__(None)

    def describe(self, level = 0):
        print "%s(%.3f, %.3f)" % (self.__class__.__name__, self.period, self.seed),
        self.describe_next()

    def __getitem__(self, t):
        random.seed(self.seed + (int)(t / self.period))
        return self.call_next(t, hueToColor(random.random()))

class ColorWheel(ColorSource):

    def __init__(self, period = 1.0, phase = 0.0, gen = None):
        if generator:
            g = gen
        else:
            g = generator.Sawtooth(period, phase)
        super(Rainbow, self).__init__(g)

    def describe(self, level = 0):
        print "%s(%.3f, %.3f, " % (self.__class__.__name__),
        self.g.describe(level+1)
        print ")",
        self.describe_next()

    def __getitem__(self, t):
        col = colorsys.hsv_to_rgb(self.g[t], 1, 1)
        return self.call_next(t, Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255)))

class Rainbow(ColorSource):

    def __init__(self, period = 1.0, phase = 0.0, gen = None):
        if generator:
            g = gen
        else:
            g = generator.Sawtooth(period, phase)
        super(Rainbow, self).__init__(g)

    def describe(self, level = 0):
        print "%s(%.3f, %.3f, " % (self.__class__.__name__),
        if self.g:
            self.g.describe(level+1)
        print ")",
        self.describe_next()

    def __getitem__(self, t):
        color = [0,0,0]

        wheel_pos = 255 - int(255 * self.g[t])
        if wheel_pos < 85:
            color[0] = int(255 - wheel_pos * 3)
            color[1] = 0
            color[2] = int(wheel_pos * 3)
        elif wheel_pos < 170:
            wheel_pos -= 85
            color[0] = 0
            color[1] = int(wheel_pos * 3)
            color[2] = 255 - int(wheel_pos * 3)
        else:
            wheel_pos -= 170
            color[0] = int(wheel_pos * 3)
            color[1] = 255 - int(wheel_pos * 3)
            color[2] = 0

        return self.call_next(t, Color(color[0], color[1], color[2]))
