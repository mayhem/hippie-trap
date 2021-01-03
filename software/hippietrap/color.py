#!/usr/bin/python

import abc
import colorsys
import math
from random import random, seed

GAMMA_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
    10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
    17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
    25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
    37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
    51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
    69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
    90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
    115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
    144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
    177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
    215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255]

seed()

def hue_to_color(hue):
    col = colorsys.hsv_to_rgb(math.fmod(hue, 1.0), 1, 1)
    return gamma(Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255)))

def random_color():
    col = colorsys.hsv_to_rgb(random(), 1, 1)
    return gamma(Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255)))

def gamma(col):
#    col[0] = gamma[col[0]]
#    col[1] = gamma[col[0]]
#    col[2] = gamma[col[0]]
    return col

class Color(object):

    def __init__(self, r, g, b):
        self.color = [int(r), int(g), int(b)]

    @property
    def r(self):
        return  self.color[0]

    @property
    def g(self):
        return  self.color[1]

    @property
    def b(self):
        return  self.color[2]

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
        self.color[0] = min(255, self.color[0] + other.color[0])
        self.color[1] = min(255, self.color[1] + other.color[1])
        self.color[2] = min(255, self.color[2] + other.color[2])

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

if __name__ == "__main__":
    c1 = Color(1,1,128)
    c2 = Color(2,2,128)
    c1 += c2
    print(c1.red, c1.green, c1.blue)
