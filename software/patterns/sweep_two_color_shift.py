#!/usr/bin/env python3

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.color import Color, ColorGenerator, random_color, hue_to_color
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time


class SweepTwoColorShiftPattern(PatternBase):

    geo = HippieTrapGeometry()
    cg = ColorGenerator()
    name = "sweep two colors"

    color_shift_between_rings = .045

    def pattern(self):
        self.trap.send_decay(ALL, 90)
        self.trap.start_pattern(ALL)

        index = 0
        hue_offset = 0.0
        stop = False

        color_rings = [ random_color(), random_color(), random_color() , random_color() ]
        while not stop:
            for bottle, angle in self.geo.enumerate_all_bottles(index % 2 == 0):
                self.trap.set_color(bottle,
                                    color_rings[self.geo.get_ring_from_bottle(bottle)],
                                    8);
                sleep(.01)
                if self.stop_thread:
                    stop = True
                    break

            index += 1
            hue_offset = math.fmod(hue_offset + .02, 1.0)
            shift = math.sin(index / self.color_shift_between_rings) / 2.0 + .50
            new_offset = math.fmod(shift, 1.0)
            color_rings.pop()
            color_rings.insert(0, hue_to_color(new_offset))

        self.trap.stop_pattern(ALL)

if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        trap.set_brightness(ALL, 100)

        p = SweepTwoColorShiftPattern(trap)
        p.pattern()
