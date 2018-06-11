#!/usr/bin/python

import abc
import colorsys
import math
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

    def __repr__(self):
        return "Color(%d,%d,%d)" % (self.color[0], self.color[1], self.color[2])

    @property
    def red(self):
        return self.color[0]

    @property
    def green(self):
        return self.color[1]

    @property
    def blue(self):
        return self.color[2]

    @abc.abstractmethod
    def __getitem__(self, i):
        return self.color[i]

    def __iadd__(self, other):
        print self, other
        self.color[0] = min(255, self.color[0] + other.color[0])
        self.color[1] = min(255, self.color[1] + other.color[1])
        self.color[2] = min(255, self.color[2] + other.color[2])
        print self

        return self

    def __eq__(self, other):
        if isinstance(other, Color):
            return (self.color[0] == other.color[0] and self.color[1] == other.color[1] and self.color[2] == other.color[2])
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Color):
            return (self.color[0] != other.color[0] or self.color[1] != other.color[1] or self.color[2] != other.color[2])
        return NotImplemented

class ColorGenerator(object):

    def __init__(self):
        self.last_hues = [ ]

    def random_color(self):
        return self.random_color_pair(0.0)[0]

    def random_color_pair(self, offset):
        while True:
            hue = random()
            bad = False 
            for old_hue in self.last_hues:
                if math.fabs(hue - old_hue) < .10:
                    bad = True
                    break

            if bad:
                continue
            else:
                break

        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        rgb2 = colorsys.hsv_to_rgb(math.fmod(hue + offset, 1.0), 1.0, 1.0)
        self.last_hues.append(hue)
        if len(self.last_hues) > 5:
            self.last_hues = self.last_hues[1:]

        return (Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])), 
                Color(int(255 * rgb2[0]), int(255 * rgb2[1]), int(255 * rgb2[2])))
