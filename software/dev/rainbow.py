#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.chandelier import Chandelier, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time

STEPS = 20000

device = "/dev/serial0"

ch = Chandelier()
ch.open(device)

while True:
    for i in range(STEPS):
        rgb = hsv_to_rgb(i / float(STEPS), 1.0, 1.0)
        ch.set_color(BROADCAST, Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))
