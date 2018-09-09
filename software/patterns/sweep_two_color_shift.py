#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.color import Color, ColorGenerator
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time


class Pattern(PatternBase):

    geo = HippieTrapGeometry()
    cg = ColorGenerator()

    def pattern(self):
        self.trap.send_decay(ALL, 10)
        self.trap.start_pattern(ALL)

        index = 0
        hue_offset = 0.0
        while True:
            col1, col2 = self.cg.random_color_pair(hue_offset)
            for bottle, angle in self.geo.enumerate_all_bottles(index % 2 == 0):
                if self.geo.get_ring_from_bottle(bottle) % 2 == 0:
                    self.trap.set_color(bottle, col1)
                else:
                    self.trap.set_color(bottle, col2)
                sleep(.02)
                if self.stop_thread:
                    return

            index += 1
            hue_offset = math.fmod(hue_offset + .01, 1.0)


if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        run_pattern(trap, Pattern, clear=True)
        trap.clear(ALL)
