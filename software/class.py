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

ch.set_classes([[1], [2, 3]])

random.seed()

green = function.ConstantColor(Color(0,255,0))
green.chain(filter.Brightness(generator.Sawtooth(2)))

blue = function.ConstantColor(Color(0,0,255))
blue.chain(filter.Brightness(generator.Sawtooth(2)))

red = function.ConstantColor(Color(255,0,0))
red.chain(filter.Brightness(generator.Sawtooth(2)))

ch.send_pattern_to_class(0, blue) 
ch.send_pattern_to_class(1, green) 
ch.send_pattern_to_class(2, red) 
ch.next_pattern(BROADCAST, 0)
ch.debug_serial(0)
