#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST
import function
import random
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

random.seed()
period_s = 1

col = [ randint(60, 255), 0, randint(60, 255) ]

while True:
    for brightness in xrange(0, 100):
        ch.set_brightness(BROADCAST, brightness)
        ch.set_color(2, col) 
        ch.debug_serial(.01)
