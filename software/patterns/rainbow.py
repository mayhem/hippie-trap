#!/usr/bin/env python3

import os
import sys
import math
from hippietrap import HippieTrap, ALL
from hippietrap.pattern import PatternBase
from hippietrap.color import SystemColors
from time import sleep, time

STEPS = 500


class RainbowPattern(PatternBase):

    name = "rainbow"

    def __init__(self, trap):
        PatternBase.__init__(self, trap)
        self.colors = SystemColors()

    def pattern(self):
        for i in range(STEPS):
            self.trap.set_color(ALL, self.colors.hue_to_color(i / float(STEPS)))
            sleep(.02)
            if self.stop_thread:
                break
