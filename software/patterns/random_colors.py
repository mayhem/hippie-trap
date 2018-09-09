#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time
from random import random
from hippietrap.transition import transition_drop_out


class Pattern(PatternBase):

    PERIOD = 450
    name = "random colors"

    def pattern(self):
        self.trap.send_entropy()
        while True:
            self.trap.send_fade(ALL, self.PERIOD, ())
            self.trap.start_pattern(ALL)
            sleep(self.PERIOD / 1000.0)
            self.trap.stop_pattern(ALL)

            if self.stop_thread:
                break 

        self.trap.stop_pattern(ALL)
        if self.transition:
            sleep(.02)
            transition_drop_out(self.trap)

if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        run_pattern(trap, Pattern)
        trap.clear(ALL)
