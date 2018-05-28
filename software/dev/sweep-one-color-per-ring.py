#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES, NUM_RINGS
from hippietrap.color import Color, ColorGenerator
from hippietrap.geometry import HippieTrapGeometry
from time import sleep, time

STEPS = 500

geo = HippieTrapGeometry()
cg = ColorGenerator()

with HippieTrap() as ch:
    try:
        while True:
            for i, ring in enumerate(range(NUM_RINGS)):
                color = cg.random_color()
                for bottle, angle in geo.enumerate_ring(ring, i % 2):
                    ch.set_color(bottle, color)
                    sleep(.04)

    except KeyboardInterrupt:
        ch.clear_cruft()
        ch.clear_cruft()
        for bottle, angle in geo.enumerate_all_bottles():
            ch.set_color(bottle, Color(0,0,0))
            sleep(.02)
