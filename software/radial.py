#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST, mkcls
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

ch.set_classes(1, range(1,11))
ch.set_classes(2, [11, 12])

random.seed()

# outer ring
for i in range(1, 12):
    angle = i / 11.0
    ch.set_angle(i, angle)

white = function.ConstantColor(Color(255, 255, 255))

blue = function.ConstantColor(Color(0, 0, 255))
blue.chain(filter.Brightness(generator.Sin(1, generator.LocalAngle())))

ch.send_pattern(mkcls(1), blue) 
ch.send_pattern(mkcls(2), white) 
ch.next_pattern(BROADCAST, 0)
ch.debug_serial(0)
