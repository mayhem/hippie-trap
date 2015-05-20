#!/usr/bin/python
import abc
import math
from common import ChainLink
from color import Color

class Filter(ChainLink):

    def __init__(self):
        self.next = None
        super(Filter, self).__init__()

    def call_filter(self, t, col):
        if self.next:
            return self.next.filter(t, col)
        return col 

    @abc.abstractmethod
    def filter(self, t, color):
        pass

class FadeIn(Filter):

    def __init__(self, duration = 1.0, offset = 0.0):
        self.duration = duration
        self.offset = offset
        super(FadeIn, self).__init__()

    def describe(self):
        print "%s(%.3f, %.3f)" % (self.__class__.__name__, self.duration, self.offset)
        self.describe_next()

    def filter(self, t, color):
        if t < self.offset:
            return Color(0,0,0)
        if t < self.offset + self.duration:
            percent = (t - self.offset) / self.duration
            return Color( int(color[0] * percent), int(color[1] * percent), int(color[2] * percent))

        return self.call_next(t, color)

class FadeOut(Filter):

    def __init__(self, duration = 1.0, offset = 0.0):
        self.duration = duration
        self.offset = offset
        super(FadeOut, self).__init__()

    def describe(self):
        print "%s(%.3f, %.3f)" % (self.__class__.__name__, self.duration, self.offset)
        self.describe_next()

    def filter(self, t, color):
        if t > self.offset + self.duration:
            return Color(0,0,0)
        if t > self.offset: 
            percent = 1.0 - ((t - self.offset) / self.duration)
            return Color( int(color[0] * percent), int(color[1] * percent), int(color[2] * percent))

        return self.call_next(t, color)

class Brightness(Filter):

    def __init__(self, gen):
        self.gen = gen
        super(Brightness, self).__init__()

    def describe(self):
        print "%s("% self.__class__.__name__,
        self.gen.describe()
        print ")"
        self.describe_next()

    def filter(self, t, color):
        percent = self.gen[t]
        return self.call_next(t, Color(int(color[0] * percent), int(color[1] * percent), int(color[2] * percent)))
