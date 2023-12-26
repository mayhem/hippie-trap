#!/usr/bin/env python3

import os
import sys
import math
from random import random, randint
from hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.pattern import PatternBase, run_pattern
from hippietrap.color import hue_to_color, random_color
from time import sleep, time

class SparklePattern(PatternBase):

    name = "sparkle"
    PERIOD = 1000

    def pattern(self):

        stop = False
        while not stop:
            bottle = randint(1, NUM_NODES)
            self.trap.set_color(bottle, random_color())
            sleep(.01)
            self.trap.send_fade(bottle, self.PERIOD, [(0,0,0),(0,0,0),(0,0,0),(0,0,0)])
            sleep(.01)
            self.trap.start_pattern(bottle)
            sleep(.01)

            if self.stop_thread:
                stop = True
                break

        self.trap.stop_pattern(ALL)
