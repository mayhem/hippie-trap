#!/usr/bin/env python

import os
import sys
import math
from random import random, randint
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.pattern import PatternBase, run_pattern
from hippietrap.color import hue_to_color
from time import sleep, time

class Pattern(PatternBase):

    name = "sparkle fuck you"

    def pattern(self):

        self.trap.start_pattern(ALL)
        stop = False
        while not stop:
            for i in range(15):
                bottle = randint(1, NUM_NODES)
                led = randint(1, 4)
                self.trap.set_color(bottle, hue_to_color(random()))

            self.trap.send_decay(ALL, 4)
            sleep(.3)

            if self.stop_thread:
                stop = True
                break

        self.trap.stop_pattern(ALL)
