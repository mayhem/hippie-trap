#!/usr/bin/python

import abc
import colorsys
import math
from random import random, seed
import hippietrap

seed()


def hue_to_color(hue):
    col = colorsys.hsv_to_rgb(math.fmod(hue, 1.0), 1, 1)
    if hippietrap.bedtime_mode:
        return Color(int(col[0] * 255), int(col[1] * 255), 0)
    else:
        return Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255))


def random_color():
    col = colorsys.hsv_to_rgb(random(), 1, 1)
    if hippietrap.bedtime_mode:
        return Color(int(col[0] * 255), int(col[1] * 255), 0)
    else:
        return Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255))


class Color(object):
    def __init__(self, r, g, b):
        self.color = [int(r), int(g), int(b)]

    @property
    def r(self):
        return self.color[0]

    @property
    def g(self):
        return self.color[1]

    @property
    def b(self):
        return self.color[2]

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
        self.last_hues = []

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

        return (Color(int(255 * rgb[0]), int(255 * rgb[1]),
                      int(255 * rgb[2])), Color(int(255 * rgb2[0]), int(255 * rgb2[1]), int(255 * rgb2[2])))


class Gradient(object):
    def __init__(self, palette, num_leds=1):

        # palletes are in format [ (.345, (128, 0, 128)) ]
        self._validate_palette(palette)
        self.palette = palette
        self.num_leds = num_leds
        self.led_scale = 1.0
        self.led_offset = 0.0

    def _validate_palette(self, palette):

        if len(palette) < 2:
            raise ValueError("Palette must have at least two points.")

        if palette[0][0] > 0.0:
            raise ValueError("First point in palette must be less than or equal to 0.0")

        if palette[-1][0] < 1.0:
            raise ValueError("Last point in palette must be greater than or equal to 1.0")

    def set_scale(self, scale):
        self.led_scale = scale

    def set_offset(self, offset):
        self.led_offset = offset

    def get_color_by_offset(self, offset):

        if offset < 0.0 or offset > 1.0:
            raise IndexError("Invalid offset.")

        for index in range(len(self.palette)):

            # skip the first item
            if index == 0:
                continue

            if self.palette[index][0] >= offset:
                section_begin_offset = self.palette[index - 1][0]
                section_end_offset = self.palette[index][0]

                percent = (offset - section_begin_offset) / (section_end_offset - section_begin_offset)
                new_color = []
                for color in range(3):
                    new_color.append(
                        int(self.palette[index - 1][1][color] +
                            ((self.palette[index][1][color] - self.palette[index - 1][1][color]) * percent)))

                return (min(new_color[0], 255), min(new_color[1], 255), min(new_color[2], 255))

        assert False
