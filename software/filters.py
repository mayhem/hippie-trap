#!/usr/bin/python
import abc
import math
from common import Color, ChainLink

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

    def filter(self, t, color):
        if t > self.offset + self.duration:
            return Color(0,0,0)
        if t > self.offset: 
            percent = 1.0 - ((t - self.offset) / self.duration)
            return Color( int(color[0] * percent), int(color[1] * percent), int(color[2] * percent))

        return self.call_next(t, color)

