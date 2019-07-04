#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES, NUM_RINGS, BOTTLES_PER_RING, group
from hippietrap.color import Color, ColorGenerator
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.pattern import PatternBase, run_pattern
from hippietrap.transition import transition_sweep_out
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

                    value = int(255 * value)
                    color = (value, 0, 0)
                    self.trap.set_color(group(ring), color)
                    sleep(.02)

            if self.stop_thread:
                stop = True
                break

        if self.transition:
            sleep(.05)
            transition_sweep_out(self.trap)
