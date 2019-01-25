#!/usr/bin/python

import os
import sys
import math
from hippietrap.hippietrap import HippieTrap, NUM_NODES, ALL, BOTTLES_PER_RING
from hippietrap.color import hue_to_color
from hippietrap.pattern import PatternBase
from time import sleep
from random import random
from hippietrap.transition import transition_sweep_out

class FireIceCirclesPattern(PatternBase):

    PERIOD = 1500
    angle = .08
    name = "fire ice circles"

    def pattern(self):

        color_offset = 0.0
        stop = False

        bottle_base = 1
        for i, ring in enumerate(BOTTLES_PER_RING):
            if i == len(BOTTLES_PER_RING):
                break

            for bottle in range(bottle_base, bottle_base + BOTTLES_PER_RING[i] + 1):
                array = []

                hue = (random() / 5) + color_offset + (i * .5)
                array.append(hue_to_color(min(1.0, math.fmod(hue, 1.0))))
                array.append(hue_to_color(min(1.0, math.fmod(hue + self.angle, 1.0))))
                array.append(hue_to_color(min(1.0, math.fmod(hue + (self.angle * 2), 1.0))))
                array.append(hue_to_color(min(1.0, math.fmod(hue + (self.angle * 3), 1.0))))

                self.trap.stop_pattern(bottle)
                self.trap.send_fade(bottle, self.PERIOD, array)
                sleep(.035)

                if self.stop_thread:
                    stop = True
                    break

                self.trap.start_pattern(bottle)

            bottle_base += BOTTLES_PER_RING[i]
            color_offset += .1

        self.trap.stop_pattern(ALL)
        if self.transition:
            sleep(.02)
            transition_sweep_out(self.trap)
