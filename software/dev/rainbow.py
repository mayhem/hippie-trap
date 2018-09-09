#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.pattern import PatternBase, run_pattern
from hippietrap.color import Color, hue_to_color
from time import sleep, time


STEPS = 500

class Rainbow(PatternBase):

    def pattern(self):
        for i in range(STEPS):
            ch.set_color(ALL, hue_to_color(i / float(STEPS)))
            sleep(.02)
            if self.stop_thread:
                return

if __name__ == "__main__":
    with HippieTrap() as ch:
        ch.begin()
        run_pattern(ch, Rainbow)
        ch.clear(ALL)
