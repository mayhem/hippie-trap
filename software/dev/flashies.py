#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time

def flash(ch, col1, col2):
    ch.set_color_array(BROADCAST, (col1, col2, col1, col2))
    sleep(.250)
    ch.set_color_array(BROADCAST, (col2, col1, col2, col1))
    sleep(.250)

def flip(ch, col1, col2):
    ch.send_fade(BROADCAST, 250, (col1, col2, col1, col2))
    ch.start_pattern(BROADCAST)
    sleep(.250)

    ch.send_fade(BROADCAST, 250, (col2, col1, col2, col1))
    ch.start_pattern(BROADCAST)
    sleep(.250)

with HippieTrap() as ch:
    try:
        while True:
            col1 = Color(255, 255, 255)

            col2 = Color(255, 0, 0)
            flip(ch, col1, col2)

            col2 = Color(255, 255, 0)
            flip(ch, col1, col2)

            col2 = Color(0, 255, 0)
            flip(ch, col1, col2)

            col2 = Color(0, 255, 255)
            flip(ch, col1, col2)

            col2 = Color(0, 0, 255)
            flip(ch, col1, col2)

    except KeyboardInterrupt:
        ch.clear_cruft()
        ch.clear(BROADCAST)
        ch.clear(BROADCAST)
