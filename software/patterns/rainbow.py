#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.pattern import PatternBase, run_pattern
from hippietrap.color import Color, hue_to_color
from hippietrap.transition import transition_drop_out
from time import sleep, time


STEPS = 500

class Pattern(PatternBase):

    name = "rainbow"

    def pattern(self):
        for i in range(STEPS):
            self.trap.set_color(ALL, hue_to_color(i / float(STEPS)))
            sleep(.02)
            if self.stop_thread:
                break

        if self.transition:
            sleep(.02)
            transition_drop_out(self.trap)

if __name__ == "__main__":
    with HippieTrap() as ch:
        ch.begin()
        run_pattern(ch, Pattern)
        ch.clear(ALL)
