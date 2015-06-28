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
wobble = function.RandomColorSequence(generator.LocalRandomValue(.5, .75), generator.LocalRandomValue(0.0, 1.00))
wobble.chain(filter.Brightness(generator.Sin(generator.RepeatLocalRandomValue(0))))

ch.send_pattern(BROADCAST, wobble) 
ch.next_pattern(BROADCAST, 0)

while True:
    for brightness in xrange(0, 100):
        ch.set_brightness(BROADCAST, brightness)
        ch.debug_serial(.1)
