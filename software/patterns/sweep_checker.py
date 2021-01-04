#!/usr/bin/env python3

import os
import sys
import math
from colour import Color as Colour
from colorsys import hsv_to_rgb
from random import random
import matplotlib as mpl
import numpy as np
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES, NUM_RINGS, BOTTLES_PER_RING
from hippietrap.color import Color, ColorGenerator, random_color, hue_to_color
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time

BOTTLE_INDEXES = [
    [ 1, 13 ],
    [ 14, 30 ],
    [ 31, 50 ],
    [ 50, 72 ],
]

# TODO: Improve this (and others) by using fade to

class SweepCheckerPattern(PatternBase):

    geo = HippieTrapGeometry()
    cg = ColorGenerator()
    name = "sweep checker"

    def pattern(self):

        bottle_states = [ ]
        for r in range(NUM_NODES + 1):
            bottle_states.append(r % 2 == 0)

        stop = False
        while not stop:
            hue = random()
            c1 = hue_to_color(hue)
            c1 = Colour(rgb=(c1[0] / 255.0, c1[1] / 255.0, c1[2] / 255.0))
            c2 = hue_to_color(hue + .5)
            c2 = Colour(rgb=(c2[0] / 255.0, c2[1] / 255.0, c2[2] / 255.0))

            gradient = []
            for c in c1.range_to(c2, 181):
                gradient.append((int(c.red * 255), int(c.green * 255), int(c.blue * 255)))

            for angle in range(181, 0, -1):
                for bottle, bottle_angle in self.geo.get_near_bottles(angle, 1):
                    if bottle_angle < angle:
                        if bottle_states[bottle]: 
                            self.trap.set_color(bottle, gradient[int(bottle_angle)])
                        else:
                            self.trap.set_color(bottle, gradient[int(180 - bottle_angle)])
                        bottle_states[bottle] =  not bottle_states[bottle]
                        sleep(.03)

            if self.stop_thread:
                stop = True
                break

if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        trap.set_brightness(ALL, 100)

        p = SweepCheckerPattern(trap)
        p.pattern()
