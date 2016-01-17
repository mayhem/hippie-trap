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

ch.set_angle(1, 0)
ch.set_angle(2, 45)

blue = function.ConstantColor(Color(0, 255, 0))
blue.chain(filter.Brightness(generator.Sin(1, generator.LocalAngle())))

ch.send_pattern(BROADCAST, blue) 
ch.next_pattern(BROADCAST, 0)
ch.debug_serial(0)
