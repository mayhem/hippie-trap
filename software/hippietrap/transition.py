#!/usr/bin/python

import os
import sys
import math
import random
import importlib
from threading import Thread
from color import Color
from hippietrap import NUM_NODES, ALL
from pattern import PatternBase, run_pattern
from geometry import HippieTrapGeometry
from time import sleep, time

geo = HippieTrapGeometry()


def transition_drop_out(trap):
    bottles = [i for i in range(1, NUM_NODES + 1)]
    random.shuffle(bottles)
    for bottle in bottles:
        trap.clear(bottle)
        sleep(.005)


def transition_sweep_out(trap):
    for bottle, angle in geo.enumerate_all_bottles():
        trap.set_color(bottle, Color(0, 0, 0))
        sleep(.005)


def transition_sweep_in(trap):
    bottles = geo.enumerate_all_bottles()
    bottles.reverse()
    for bottle, angle in bottles:
        trap.set_color(bottle, Color(0, 0, 0))
        sleep(.005)


def transition_fade_out(trap):
    trap.send_decay(ALL, 10)
    trap.start_pattern(ALL)
    sleep(.2)
    trap.stop_pattern(ALL)


def transition_lateral_sweep(trap):
    bottles = geo.calculate_bottle_locations()
    bottles = list(zip(list(range(1, NUM_NODES + 1)), bottles))
    bottles.sort(key=lambda bottles: bottles[1][0])
    for bottle, coord in bottles:
        trap.set_color(bottle, Color(0, 0, 0))
        sleep(.001)
