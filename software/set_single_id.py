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

device = "/dev/ttyAMA0"

if len(sys.argv) == 2:
    id = int(sys.argv[1])
else:
    print "Usage: %s <id>" % (sys.argv[0])
    sys.exit(-1)

print "Programming id %d" % id

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)
ch.set_id(id)
