#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES, NUM_RINGS
from hippietrap.color import Color, ColorGenerator
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time


class Pattern(PatternBase):

    geo = HippieTrapGeometry()
    cg = ColorGenerator()

    def pattern(self):
        while True:
            for i, ring in enumerate(range(NUM_RINGS)):
                color = self.cg.random_color()
                for bottle, angle in self.geo.enumerate_ring(ring, i % 2):
                    self.trap.set_color(bottle, color)
                    sleep(.04)
                    if self.stop_thread:
                        return


if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        run_pattern(trap, Pattern)
        trap.clear(ALL)
