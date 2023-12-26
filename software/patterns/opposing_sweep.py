#!/usr/bin/env python3

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap import HippieTrap, ALL, NUM_NODES, NUM_RINGS, BOTTLES_PER_RING
from hippietrap.color import Color, ColorGenerator, SystemColors
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time

# TODO: ALternating rings come towards each other.
# TODO: Never exit until full cycle is complete

# BOTTLES_PER_RING = (13, 17, 19, 23)

BOTTLE_INDEXES = [
    [1, 13],
    [14, 30],
    [31, 50],
    [50, 72],
]


def rf(offset, max_range):
    return offset + (random() * max_range)


class OpposingSweepPattern(PatternBase):

    geo = HippieTrapGeometry()
    cg = ColorGenerator()
    name = "opposing sweep"

    def __init__(self, trap):
        PatternBase.__init__(self, trap)
        self.colors = SystemColors()

    def pattern(self):

        hue = random()
        hue2 = random()
        hue_offset = rf(.01, .01)
        hue_offset2 = rf(.01, .01)

        self.trap.send_decay(ALL, 95)
        self.trap.start_pattern(ALL)
        stop = False
        while not stop:
            color_rings = [
                self.colors.hue_to_color(hue),
                self.colors.hue_to_color(hue + hue_offset + rf(.5, .15)),
                self.colors.hue_to_color(hue2),
                self.colors.hue_to_color(hue2 + hue_offset + rf(.5, .35))
            ]
            for angle in range(180):
                for bottle, bottle_angle in self.geo.get_near_bottles(angle, 1):
                    ring = self.geo.get_ring_from_bottle(bottle)
                    if ring % 2 == 1:
                        bottle = BOTTLE_INDEXES[ring][1] - (bottle - BOTTLE_INDEXES[ring][0])

                    if bottle_angle >= angle:
                        color = color_rings[ring]
                        self.trap.set_color(bottle, color, 6)

                        sleep(.01)
            hue = math.fmod(hue + rf(.05, .15), 1.0)
            hue2 = math.fmod(hue + rf(.03, .15), 1.0)

            if self.stop_thread:
                stop = True
                break

        self.trap.stop_pattern(ALL)


if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        trap.set_brightness(ALL, 100)

        p = OpposingSweepPattern(trap)
        p.pattern()
