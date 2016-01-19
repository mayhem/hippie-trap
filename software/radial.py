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

ch.set_classes([range(1,12), [12]])

random.seed()

# outer ring
for i in range(1, 12):
    angle = i / 11.0
    ch.set_angle(i, angle)

def circular_random_colors(ch):
    white = function.ConstantColor(Color(255, 255, 255))
    white.chain(filter.Brightness(generator.Sin(2, 0, .2, .6)))

    radial = function.RandomColorSequence(generator.LocalRandomValue(1.0, 1.50), generator.LocalRandomValue(0.0, 1.00))
    radial.chain(filter.Brightness(generator.Sin(1, generator.LocalAngle())))

    ch.send_pattern_to_class(0, radial) 
    ch.send_pattern_to_class(1, white) 
    ch.next_pattern(BROADCAST, 0)

def circular_rainbow(ch):
    white = function.ConstantColor(Color(255, 255, 255))
    white.chain(filter.Brightness(generator.Sin(2, 0, .2, .6)))

    radial = function.HSV(generator.Sawtooth(5))
#    radial.chain(filter.Brightness(generator.Sin(1, generator.GenOp(common.OP_MUL, generator.LocalAngle(), generator.Constant(1)))))
    radial.chain(filter.Brightness(generator.Sin(1, generator.LocalAngle())))

    ch.send_pattern_to_class(0, radial) 
    ch.send_pattern_to_class(1, white) 
    ch.next_pattern(BROADCAST, 0)

circular_rainbow(ch)
