#!/usr/bin/python

import os
import sys
import math
from hippietrap.hippietrap import HippieTrap, BROADCAST
from hippietrap.color import Color
from random import randint, seed
from time import sleep, time

DELAY = .02

device = "/dev/serial0"

ch = HippieTrap()
ch.open(device)
ch.off(BROADCAST)
ch.send_entropy()
ch.set_brightness(BROADCAST, 100)

seed()
period_s = 1

col = [ randint(60, 255), 0, randint(60, 255) ]
print col

while True:
    for brightness in xrange(0, 100):
        print("%d" % brightness)
        ch.set_brightness(BROADCAST, brightness)
        ch.set_color(BROADCAST, col) 
        sleep(.1)
