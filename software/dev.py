#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST
from function import Pattern, Function
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

p = Pattern(10,
        Function(common.FUNC_SQUARE, 13, 1.0, 0.0, 1.0, 0.0, .6),
        Function(common.FUNC_SQUARE, 14, .8, 0.0, 1.0, 0.0, .5),
        Function(common.FUNC_SQUARE, 15, .6, 0.0, 1.0, 0.0, .4)
)
ch.send_pattern(2, p)
ch.start_pattern(2)
