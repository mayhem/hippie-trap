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

    def describe(self, level = 0):
        #print "%s(%d, %d, %d)" % (self.__class__.__name__, self.color[0], self.color[1]. self.color[2]),
        pass

    def __str__(self):
        return "Color(%d,%d,%d)" % (self.color[0], self.color[1], self.color[2])

    @abc.abstractmethod
    def __getitem__(self, i):
        return self.color[i]

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
