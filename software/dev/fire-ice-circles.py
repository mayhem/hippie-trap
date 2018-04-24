#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time
from random import random

PERIOD = 1500

device = "/dev/serial0"

ch = HippieTrap()
ch.open(device)

angle = .04

try:
    color_offset = 0.0
    while True:
        for bottle in range(1, 14):
            array = []

            hue = (random() / 5) + color_offset
            rgb = hsv_to_rgb(min(1.0, math.fmod(hue, 1.0)), 1, 1)
            array.append(Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))

            rgb = hsv_to_rgb(min(1.0, math.fmod(hue + angle, 1.0)), 1, 1)
            array.append(Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))

            rgb = hsv_to_rgb(min(1.0, math.fmod(hue + (angle * 2), 1.0)), 1, 1)
            array.append(Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))

            rgb = hsv_to_rgb(min(1.0, math.fmod(hue + (angle * 3), 1.0)), 1, 1)
            array.append(Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))

            ch.stop_pattern(bottle)
            ch.send_fade(bottle, PERIOD, array)
            ch.start_pattern(bottle)

        for bottle in range(14, 31):
            array = []

            hue = (random() / 5) + color_offset + .5
            rgb = hsv_to_rgb(min(1.0, math.fmod(hue, 1.0)), 1, 1)
            array.append(Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))

            rgb = hsv_to_rgb(min(1.0, math.fmod(hue + angle, 1.0)), 1, 1)
            array.append(Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))

            rgb = hsv_to_rgb(min(1.0, math.fmod(hue + (angle * 2), 1.0)), 1, 1)
            array.append(Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))

            rgb = hsv_to_rgb(min(1.0, math.fmod(hue + (angle * 3), 1.0)), 1, 1)
            array.append(Color(int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2])))

            ch.stop_pattern(bottle)
            ch.send_fade(bottle, PERIOD, array)
            ch.start_pattern(bottle)

        color_offset += .01

except KeyboardInterrupt:
    ch.clear_cruft()
    ch.fade_out(BROADCAST)
