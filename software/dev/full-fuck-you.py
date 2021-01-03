#!/usr/bin/env python3

import os
import sys
import math
from random import random, randint
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time

PERIOD = 500

with HippieTrap() as ch:
    ch.begin()
    ch.send_entropy()
    ch.send_decay(BROADCAST, 16);
    ch.start_pattern(BROADCAST)

    try:
        while True:
            for i in range(NUM_NODES):
                ch.set_random_color(randint(1, NUM_NODES))
                sleep(.003)

    except KeyboardInterrupt:
        ch.stop_pattern(BROADCAST)
        ch.clear(BROADCAST)
