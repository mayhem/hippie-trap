#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color, hue_to_color
from time import sleep, time

STEPS = 500

with HippieTrap() as ch:
    ch.begin()
    try:
        while True:
            for i in range(STEPS):
                ch.set_color(BROADCAST, hue_to_color(i / float(STEPS)))
                sleep(.02)

    except KeyboardInterrupt:
        ch.clear_cruft()
        ch.clear(BROADCAST)
        ch.clear(BROADCAST)
