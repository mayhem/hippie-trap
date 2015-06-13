#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST
import function
import generator
import filter
import random
from time import sleep, time
from color import Color

device = "/dev/ttyAMA0"
if len(sys.argv) == 2:
    device = sys.argv[1]

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)
