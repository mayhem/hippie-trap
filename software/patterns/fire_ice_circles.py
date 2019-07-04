#!/usr/bin/python

import os
import sys
import math
from hippietrap.hippietrap import HippieTrap, NUM_NODES, ALL, BOTTLES_PER_RING
from hippietrap.color import hue_to_color
from hippietrap.pattern import PatternBase
from time import sleep
from random import random
from hippietrap.transition import transition_sweep_in

class FireIceCirclesPattern(PatternBase):

    PERIOD = 1500
    angle = .08
    name = "fire ice circles"

    def pattern(self):

        color_shift = 0.0
        color_offset = 0.0
        stop = False

        while True:
            bottle_base = 1
            for i, ring in enumerate(BOTTLES_PER_RING):
                if i == len(BOTTLES_PER_RING):
                    break

                for bottle in range(bottle_base, bottle_base + BOTTLES_PER_RING[i] + 1):
                    array = []

                    #                                   This last part makes each ring distinct
                    hue = color_shift + (random() / 4) + color_offset  + (i * .1)
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

                if self.stop_thread:
                    stop = True
                    break
                bottle_base += BOTTLES_PER_RING[i]
                color_offset += .1

            if self.stop_thread:
                stop = True
                break
            color_shift += .01

        self.trap.stop_pattern(ALL)
        if self.transition:
            sleep(.02)
            transition_sweep_in(self.trap)
