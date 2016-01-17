#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST, NUM_NODES
import function
import generator
import filter
import random
import common
from time import sleep, time
from color import Color

device = "/dev/ttyAMA0"

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)

for id in range(1,NUM_NODES):
    ch.set_color(id, Color(0,0,0))

for id in range(1,NUM_NODES):
    ch.set_color(id, Color(0,0,255))
    sleep(.25)
