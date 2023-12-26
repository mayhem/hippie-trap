#!/usr/bin/env python3

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.pattern import PatternBase, run_pattern
from hippietrap.color import Color, hue_to_color
from time import sleep, time


STEPS = 500

class SolidPattern(PatternBase):

    name = "solid"

    def __init__(self, trap):
        super(PatternBase, self).__init__()
        self.trap = trap
        self.trap.set_color(ALL, Color(48, 0, 48))


    def pattern(self):
        while not self.stop_thread:
            sleep(.1)


    def set_color(self, color):
        self.trap.set_color(ALL, color)
