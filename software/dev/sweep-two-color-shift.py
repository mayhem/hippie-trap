#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color, ColorGenerator
from hippietrap.geometry import HippieTrapGeometry
from time import sleep, time

STEPS = 500

geo = HippieTrapGeometry()
cg = ColorGenerator()

old_bottles = []

NUM_DECAYS = 3

with HippieTrap() as ch:
    try:
        ch.send_decay(BROADCAST, 7)
        ch.start_pattern(BROADCAST)

        index = 0
        hue_offset = 0.0
        while True:
            col1, col2 = cg.random_color_pair(hue_offset)
            for bottle, angle in geo.enumerate_all_bottles(index % 2 == 0):
                if geo.get_ring_from_bottle(bottle) % 2 == 0:
                    ch.set_color(bottle, col1)
                else:
                    ch.set_color(bottle, col2)
                sleep(.02)
            index += 1
            hue_offset = math.fmod(hue_offset + .01, 1.0)


    except KeyboardInterrupt:
        ch.clear_cruft()
        ch.clear_cruft()
        ch.stop_pattern(BROADCAST)
        for bottle, angle in geo.enumerate_all_bottles():
            ch.set_color(bottle, Color(0,0,0))
            sleep(.02)
