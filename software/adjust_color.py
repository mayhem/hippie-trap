#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST
import function
import generator
import filter
import random
import common
from time import sleep, time
from color import Color

DELAY = .02

device = "/dev/ttyAMA0"

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)
ch.send_entropy()

random.seed()
green = function.ConstantColor(Color(0,255,0))
green.chain(filter.Brightness(generator.Sawtooth(1)))

ch.send_pattern(BROADCAST, green) 
ch.next_pattern(BROADCAST, 0)

while True:
    for hue in xrange(0, 100):
        ch.set_color_filter(BROADCAST, hue, 0, 0)
        ch.debug_serial(.1)
