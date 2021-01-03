#!/usr/bin/env python3

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES, NUM_RINGS, BOTTLES_PER_RING
from hippietrap.color import Color, ColorGenerator
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time

# TODO: ALternating rings come towards each other. 
# TODO: Never exit until full cycle is complete

# BOTTLES_PER_RING = (13, 17, 19, 23)


BOTTLE_INDEXES = [
    [ 1, 13 ],
    [ 14, 30 ],
    [ 31, 50 ],
    [ 50, 72 ],
]


class SweepOneColorPerRingPattern(PatternBase):

    geo = HippieTrapGeometry()
    cg = ColorGenerator()
    name = "sweep one color"

    def pattern(self):
        self.trap.send_decay(ALL, 95)
        self.trap.start_pattern(ALL)
        stop = False
        while not stop:
            for angle in range(180):
                for bottle, bottle_angle in self.geo.get_near_bottles(angle, 1):
                    ring = self.geo.get_ring_from_bottle(bottle)
                    if ring % 2 == 1:
                        bottle = BOTTLE_INDEXES[ring][1] - (bottle - BOTTLE_INDEXES[ring][0])

                    if bottle_angle >= angle:
                        color = self.cg.random_color()
                        self.trap.set_color(bottle, color)
                        
                        sleep(.01)

            if self.stop_thread:
                stop = True
                break

        self.trap.stop_pattern(ALL)
