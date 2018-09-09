#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, NUM_NODES, ALL
from hippietrap.color import hue_to_color
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time
from random import random
from hippietrap.transition import transition_sweep_out

class Pattern(PatternBase):

    PERIOD = 1500
    angle = .02
    name = "fire ice circles"

    def pattern(self):

        color_offset = 0.0
        stop = False
        while not stop:
            for bottle in range(1, 14):
                array = []

                # refactor this copypasta!
                hue = (random() / 5) + color_offset
                array.append(hue_to_color(min(1.0, math.fmod(hue, 1.0))))
                array.append(hue_to_color(min(1.0, math.fmod(hue + self.angle, 1.0))))
                array.append(hue_to_color(min(1.0, math.fmod(hue + (self.angle * 2), 1.0))))
                array.append(hue_to_color(min(1.0, math.fmod(hue + (self.angle * 3), 1.0))))

                self.trap.stop_pattern(bottle)
                self.trap.send_fade(bottle, self.PERIOD, array)
                sleep(.035)
                self.trap.start_pattern(bottle)

                if self.stop_thread:
                    stop = True
                    break

            for bottle in range(14, 31):
                array = []

                hue = (random() / 5) + color_offset + .5
                array.append(hue_to_color(min(1.0, math.fmod(hue, 1.0))))
                array.append(hue_to_color(min(1.0, math.fmod(hue + self.angle, 1.0))))
                array.append(hue_to_color(min(1.0, math.fmod(hue + (self.angle * 2), 1.0))))
                array.append(hue_to_color(min(1.0, math.fmod(hue + (self.angle * 3), 1.0))))

                self.trap.stop_pattern(bottle)
                self.trap.send_fade(bottle, self.PERIOD, array)
                sleep(.035)
                self.trap.start_pattern(bottle)
            
                if self.stop_thread:
                    stop = True
                    break

            color_offset += .2

        self.trap.stop_pattern(ALL)
        if self.transition:
            sleep(.02)
            transition_sweep_out(self.trap)


if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        run_pattern(trap, Pattern)
        trap.clear(ALL)
