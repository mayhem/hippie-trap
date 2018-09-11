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
from hippietrap.transition import transition_sweep_out
from time import sleep, time

# TODO: ALternating rings come towards each other. 
# TODO: Never exit until full cycle is complete


class Pattern(PatternBase):

    geo = HippieTrapGeometry()
    cg = ColorGenerator()
    name = "sweep one color"

    def pattern(self):
        self.trap.send_decay(ALL, 8)
        self.trap.start_pattern(ALL)
        stop = False
        while not stop:
            for i, ring in enumerate(range(NUM_RINGS)):
                color = self.cg.random_color()
                for bottle, angle in self.geo.enumerate_ring(ring, i % 2):
                    self.trap.set_color(bottle, color)
                    sleep(.04)
                if self.stop_thread:
                    stop = True
                    break

        self.trap.stop_pattern(ALL)
        if self.transition:
            sleep(.05)
            transition_sweep_out(self.trap)

if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        run_pattern(trap, Pattern)
        trap.clear(ALL)
