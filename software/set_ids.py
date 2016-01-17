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

start_id = 1
if len(sys.argv) == 2:
    start_id = int(sys.argv[1])
else:
    print "Usage: %s <start_id>" % (sys.argv[0])
    sys.exit(-1)

print "Starting with id %d" % start_id

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)

id = start_id
while True:
    inp = raw_input("Hit enter to program node %d" % id)
    if inp.startswith("q"):
        break

    ch.set_id(id)

    id += 1

print "done"
