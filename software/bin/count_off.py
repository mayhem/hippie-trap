#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST, NUM_NODES
import function
import generator
import random
import common
from time import sleep, time
from color import Color

device = "/dev/serial0"

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)

start = int(sys.argv[1])

for id in range(start,NUM_NODES+1):
    ch.set_color(id, Color(0,0,0))

for id in range(start,NUM_NODES+1):
    print id
    ch.set_color(id, Color(0,0,255))
    sleep(.25)
