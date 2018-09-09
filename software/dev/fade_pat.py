#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time
from random import random

with HippieTrap() as ch:
    ch.begin()
    ch.set_color(BROADCAST, Color(0, 0, 0))
    try:
        while True:
            ch.send_fade(BROADCAST, 1000, (Color(128, 0, 0), ))
            ch.start_pattern(BROADCAST)
            sleep(1)

            ch.stop_pattern(BROADCAST)
            ch.send_fade(BROADCAST, 1000, (Color(0, 0, 128), ))
            ch.start_pattern(BROADCAST)
            sleep(1)

            ch.stop_pattern(BROADCAST)
            ch.send_fade(BROADCAST, 1000, (Color(128, 0, 0), ))
            ch.start_pattern(BROADCAST)
            sleep(1)

    except KeyboardInterrupt:
        ch.clear(BROADCAST)
        ch.clear(BROADCAST)
