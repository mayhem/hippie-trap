#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES, NUM_RINGS, BOTTLES_PER_RING, group
from hippietrap.color import Color, ColorGenerator, random_color
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time

# BOTTLES_PER_RING = (13, 17, 19, 23)

BOTTLE_INDEXES = [
    [ 1, 13 ],
    [ 14, 30 ],
    [ 31, 50 ],
    [ 51, 72 ],
]

class SpreadOutwardPattern(PatternBase):

    geo = HippieTrapGeometry()
    cg = ColorGenerator()
    name = "outward"

    def __init__(self, trap):
        PatternBase.__init__(self, trap)

        groups = []
        for begin, end in BOTTLE_INDEXES:
            groups.append(list(range(begin, end+1)))

        self.trap.set_groups(groups)
        

    def pattern(self):
        stop = False
        while not stop:

            color = random_color()
            for radius100 in range(-100, 100 * (NUM_RINGS + 1), 10):
                radius = radius100 / 100.0 
                for ring in range(-1, NUM_RINGS + 1):
                    if radius >= ring - 1.0 and radius <= ring:
                        value = radius - (ring - 1.0)
                    elif radius >= ring and radius <= ring + 1.0:
                        value = (ring + 1.0) - radius
                    else:
                        continue

                    if ring < 0:
                        continue

                    self.trap.set_color(group(ring), (int(color[0] * value), int(color[1] * value), int(color[2] * value)))
                    sleep(.02)

            if self.stop_thread:
                stop = True
                break
