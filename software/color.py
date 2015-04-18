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

    def __str__(self):
        return "Color(%d,%d,%d)" % (self.color[0], self.color[1], self.color[2])

    @abc.abstractmethod
    def __getitem__(self, i):
        return self.color[i]

class RandomColorSequence(object):
    '''
       Return colors that appear _random_ to a human.
    '''

    def __init__(self):
        self.last = random()

    def get(self):
        hue = (self.last + .5 + (random() * .5 - .25)) % 1.0
        col = hueToColor(hue)
        self.last = hue
        return col
