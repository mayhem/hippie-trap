#!/usr/bin/env python3

import os
import sys
import math
from hippietrap.hippietrap import HippieTrap, ALL
from hippietrap.pattern import PatternBase
from hippietrap.color import hue_to_color
from time import sleep, time


STEPS = 500

class RainbowPattern(PatternBase):

    name = "rainbow"

    def pattern(self):
        for i in range(STEPS):
            self.trap.set_color(ALL, hue_to_color(i / float(STEPS)))
            sleep(.02)
            if self.stop_thread:
                break
