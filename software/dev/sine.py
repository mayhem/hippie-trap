#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.chandelier import Chandelier, BROADCAST, NUM_NODES
from hippietrap.color import Color
from hippietrap.function import sine, Pattern
from hippietrap.common import DEST_ALL_RED
from time import sleep, time

STEPS = 500

device = "/dev/serial0"

ch = Chandelier()
ch.open(device)

p = Pattern(1, sine(DEST_ALL_RED, 1.0, 0.0, 1.0, 0.0))

try:
    ch.send_pattern(BROADCAST, p)
    ch.start_pattern(BROADCAST)
except KeyboardInterrupt:
    ch.clear(BROADCAST)
    ch.clear(BROADCAST)
