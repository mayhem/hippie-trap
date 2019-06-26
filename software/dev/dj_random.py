#!/usr/bin/python

import os
import sys
import math
import random
import abc
import importlib
from threading import Thread
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.color import Color, random_color
from hippietrap.pattern import PatternBase, run_pattern
from hippietrap.geometry import HippieTrapGeometry
from time import sleep, time

from hippietrap.patterns.rainbow import RainbowPattern
from hippietrap.patterns.solid import SolidPattern
from hippietrap.patterns.fire_ice_circles import FireIceCirclesPattern
from hippietrap.patterns.each_bottle_one_rainbow import EachBottleOneRainbowPattern
from hippietrap.patterns.random_colors import RandomColorsPattern
from hippietrap.patterns.swappies import SwappiesPattern
from hippietrap.patterns.sweep_one_color_per_ring import SweepOneColorPerRingPattern
from hippietrap.patterns.sweep_two_color_shift import SweepTwoColorShiftPattern
from hippietrap.patterns.texture import TexturePattern

geo = HippieTrapGeometry()

if len(sys.argv) == 2:
    brightness = int(sys.argv[1])
else:
    brightness = 100


def transition_drop_out(trap):
    bottles = [ i for i in range(1, NUM_NODES + 1) ]
    random.shuffle(bottles)
    for bottle in bottles:
        trap.clear(bottle)
        sleep(.01)

def transition_sweep_clear(trap):
    for bottle, angle in geo.enumerate_all_bottles():
        trap.set_color(bottle, Color(0,0,0))
        sleep(.02)


def main(transitions = True):

    with HippieTrap() as trap:
        trap.begin()
        trap.set_brightness(ALL, brightness)

        ht.add_pattern(SweepTwoColorShiftPattern)
        ht.add_pattern(SweepOneColorPerRingPattern)
        ht.add_pattern(SwappiesPattern)
        ht.add_pattern(RandomColorsPattern)
        ht.add_pattern(EachBottleOneRainbowPattern)
        ht.add_pattern(FireIceCirclesPattern)
        ht.add_pattern(SolidPattern)
        ht.add_pattern(RainbowPattern)
        ht.add_pattern(TexturePattern)
        ht.setup()

        while True:
            random.shuffle(patterns)
            for pattern_class in patterns:
                pattern = pattern_class(trap)
                print(pattern.name)
                pattern.start()
                try:
                    sleep(10)
                except KeyboardInterrupt:
                    pattern.stop()
                    pattern.join()
                    trap.clear(ALL)
                    return

                pattern.stop(transition=transitions)
                pattern.join()


if __name__ == "__main__":
    main()
