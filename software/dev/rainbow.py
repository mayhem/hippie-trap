#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time

STEPS = 5000

with HippieTrap() as ch:
    try:
        t = 0
        while True:
            for i in range(STEPS):
                rgb = hsv_to_rgb(i / float(STEPS), 1.0, 1.0)
                ch.set_color(BROADCAST, Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))
                ch.set_brightness(BROADCAST, (t / 4) % 100)
                t += 1
                sleep(.02)
    except KeyboardInterrupt:
        ch.clear_cruft()
        ch.clear(BROADCAST)
        ch.clear(BROADCAST)
