#!/usr/bin/python

import abc
import colorsys
from random import random, seed

seed()

def hueToColor(hue):
    col = colorsys.hsv_to_rgb(hue, 1, 1)
    return Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255))

def randomSaturatedColor():
    col = colorsys.hsv_to_rgb(random(), 1, 1)
    return Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255))

class Color(object):

    def __init__(self, r, g, b):
        self.color = [r, g, b]

    def describe(self, level = 0):
        print "%s(%d, %d, %d)" % (self.__class__.__name__, self.color[0], self.color[1]. self.color[2]),

    def __str__(self):
        return "Color(%d,%d,%d)" % (self.color[0], self.color[1], self.color[2])

    @abc.abstractmethod
    def __getitem__(self, i):
        return self.color[i]

