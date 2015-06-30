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
ch.set_brightness(BROADCAST, 100)

random.seed()

for i in xrange(1, 6):
    ch.set_color(i, Color(255, 0, 0))
    sleep(.21)

ch.set_position(1, -.6, 0, 0)
ch.set_position(2, -.3, 0, 0)
ch.set_position(3, .0, 0, 0)
ch.set_position(4, .3, 0, 0)
ch.set_position(5, .6, 0, 0)

xyz = function.XYZSource(generator.Sawtooth(3, 0, 1, 1), 
                         generator.Constant(0), 
                         function.XYZ_HSV, 
                         generator.Sin(1),
                         generator.Constant(.8), 
                         generator.Constant(.8))

ch.send_pattern(BROADCAST, xyz) 
ch.next_pattern(BROADCAST, 0)
ch.debug_serial(0)
