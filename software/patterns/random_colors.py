#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time
from random import random


class RandomColors(PatternBase):

    PERIOD = 450

    def pattern(self):
        trap.send_entropy()
        while True:
            trap.send_fade(ALL, self.PERIOD, ())
            trap.start_pattern(ALL)
            sleep(self.PERIOD / 1000.0)
            trap.stop_pattern(ALL)

            if self.stop_thread:
                return 


if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        run_pattern(trap, RandomColors)
        trap.clear(ALL)
