#!/usr/bin/env python3

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap import HippieTrap, ALL, NUM_NODES, NUM_RINGS, BOTTLES_PER_RING
from hippietrap.color import Color, SystemColors, Gradient
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time

BOTTLE_INDEXES = [
    [1, 13],
    [14, 30],
    [31, 50],
    [50, 72],
]


class SweepGradientPattern(PatternBase):

    geo = HippieTrapGeometry()
    name = "sweep gradient"

    def __init__(self, trap):
        PatternBase.__init__(self, trap)
        self.colors = SystemColors()

    def pattern(self):
        stop = False
        while not stop:
            c0 = self.colors.random_color()
            c1 = self.colors.random_color()
            c2 = self.colors.random_color()

            g = Gradient([ (0.0, c0), (.5, c1), (1.0, c2) ])

            for angle in range(181, 0, -1):
                for bottle, bottle_angle in self.geo.get_near_bottles(angle, 1):
                    if bottle_angle < angle:
                        self.trap.set_color(bottle, g.get_color(bottle_angle / 180.0))
                        sleep(.01)

            if self.stop_thread:
                stop = True
                break
