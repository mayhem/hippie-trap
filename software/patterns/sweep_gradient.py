#!/usr/bin/env python3

import os
import sys
import math
from colour import Color as Colour
from colorsys import hsv_to_rgb
from random import random
from hippietrap import HippieTrap, ALL, NUM_NODES, NUM_RINGS, BOTTLES_PER_RING
from hippietrap.color import Color, ColorGenerator, random_color
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time

BOTTLE_INDEXES = [
    [ 1, 13 ],
    [ 14, 30 ],
    [ 31, 50 ],
    [ 50, 72 ],
]

class SweepGradientPattern(PatternBase):

    geo = HippieTrapGeometry()
    cg = ColorGenerator()
    name = "sweep gradient"

    def pattern(self):
        stop = False
        while not stop:
            c1 = random_color()
            c1 = Colour(rgb=(c1[0] / 255.0, c1[1] / 255.0, c1[2] / 255.0))
            c2 = random_color()
            c2 = Colour(rgb=(c2[0] / 255.0, c2[1] / 255.0, c2[2] / 255.0))

            gradient = []
            for c in c1.range_to(c2, 181):
                gradient.append((int(c.red * 255), int(c.green * 255), int(c.blue * 255)))

            for angle in range(181, 0, -1):
                for bottle, bottle_angle in self.geo.get_near_bottles(angle, 1):
                    if bottle_angle < angle:
                        self.trap.set_color(bottle, gradient[int(bottle_angle)])
                        sleep(.01)

            if self.stop_thread:
                stop = True
                break

