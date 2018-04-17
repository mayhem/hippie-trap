#!/usr/bin/env python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.chandelier import Chandelier, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time

STEPS = 500

device = "/dev/serial0"

ch = Chandelier()
ch.open(device)

while True:

    for i in range(5):
        bottle = randomint(1, NUM_NODES)
        led = randomint(1, NUM_LEDS)
        hue = random()
        rgb = hsv_to_rgb(i / float(STEPS), 1.0, 1.0)
        ch.set_single_led(bottle, led, Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))

    ch.decay(BROADCAST)
    sleep(.2)
