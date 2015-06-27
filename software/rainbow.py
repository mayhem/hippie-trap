#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST
import function
import generator

device = "/dev/ttyAMA0"
if len(sys.argv) == 2:
    device = sys.argv[1]

ch = Chandelier()
ch.open(device)
rainbow = function.Rainbow(generator.Sawtooth(1))
ch.send_pattern(BROADCAST, rainbow)
ch.next_pattern(BROADCAST, 0)
