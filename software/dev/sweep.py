#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from hippietrap.geometry import HippieTrapGeometry
from time import sleep, time

STEPS = 500

geo = HippieTrapGeometry()

with HippieTrap() as ch:
    try:
        rgb = hsv_to_rgb(random(), 1.0, 1.0)
        for bottle, angle in geo.enumerate_all_bottles():
            ch.set_color(bottle, rgb)
            sleep(.02)

    except KeyboardInterrupt:
        ch.clear_cruft()
        ch.clear_cruft()
        for bottle, angle in geo.enumerate_all_bottles():
            ch.set_color(bottle, Color(0,0,0))
            sleep(.02)
