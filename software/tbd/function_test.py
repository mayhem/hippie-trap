#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST
from function import Pattern, sine, square
import common
from random import randint
from time import sleep, time
from color import Color

DELAY = .02

device = "/dev/serial0"

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)
ch.send_entropy()
ch.set_brightness(BROADCAST, 100)

# TODO:
#   - check impulse
#   - fix sin

p1 = Pattern(10,
        square(13, .5),
)

try:
    ch.send_pattern(2, p1)
    ch.start_pattern(2)
    sleep(1000000)
except KeyboardInterrupt:
    ch.off(2)
