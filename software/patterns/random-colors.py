#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time
from random import random

PERIOD = 250

with HippieTrap() as ch:
    ch.clear(BROADCAST)
    ch.send_entropy()

    try:
        while True:
            ch.send_fade(BROADCAST, PERIOD, ())
            ch.start_pattern(BROADCAST)
            sleep(PERIOD / 1000.0)
            ch.stop_pattern(BROADCAST)

    except KeyboardInterrupt:
        ch.stop_pattern(BROADCAST)
        ch.clear(BROADCAST)
