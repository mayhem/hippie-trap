#!/usr/bin/env python

import os
import sys
import math
from random import random, randint
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time

STEPS = 500

with HippieTrap() as ch:
    while True:

        for i in range(15):
            bottle = randint(1, NUM_NODES)
            led = randint(1, 4)
            hue = random()
            rgb = hsv_to_rgb(hue, 1.0, 1.0)
            ch.set_color(bottle, Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))

<<<<<<< HEAD
        ch.decay(BROADCAST)
        sleep(.5)
=======
ch.send_decay(BROADCAST, 10);
ch.start_pattern(BROADCAST)

try:
    while True:
        bottle = randint(1, NUM_NODES)
        led = randint(1, 4)
        hue = random()
        rgb = hsv_to_rgb(hue, 1.0, 1.0)
        ch.set_color(bottle, Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))
        sleep(.050)

except KeyboardInterrupt:
    ch.stop_pattern(BROADCAST)
    ch.clear(BROADCAST)
>>>>>>> bd02cc519469f00ef1db7381e87bafacc9d875d0
