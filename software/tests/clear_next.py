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
red = function.ConstantColor(Color(255,0,0))
red.chain(filter.Brightness(generator.Sawtooth(2)))

green = function.ConstantColor(Color(0,255,0))
green.chain(filter.Brightness(generator.Sawtooth(2)))

blue = function.ConstantColor(Color(0,0,255))
blue.chain(filter.Brightness(generator.Sawtooth(2)))

ch.send_pattern(BROADCAST, red) 
ch.next_pattern(BROADCAST, 0)

sleep(3);

ch.send_pattern(BROADCAST, green) 
ch.clear_next_pattern(BROADCAST)

ch.send_pattern(BROADCAST, blue) 
ch.next_pattern(BROADCAST, 0)

sleep(3);

ch.send_pattern(BROADCAST, red) 
ch.next_pattern(BROADCAST, 0)

