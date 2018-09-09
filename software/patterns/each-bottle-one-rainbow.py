#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time
from random import random

STEPS = 5000

with HippieTrap() as ch:
    ch.set_brightness(BROADCAST, 100)
    ch.clear(BROADCAST)
    ch.send_entropy()
    ch.send_rainbow(BROADCAST, 4)
    ch.start_pattern(BROADCAST)

    try:
        while True:
            sleep(1000)
    except KeyboardInterrupt:
        ch.stop_pattern(BROADCAST)
        ch.clear(BROADCAST)
