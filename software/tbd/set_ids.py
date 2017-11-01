#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST
import generator as g
import filter as f
import random
import common
import function as s
from time import sleep, time
from color import Color

device = "/dev/ttyAMA0"

confirm = raw_input("This will clear all ids of all the bottles currently plugged in. Are you sure you want this? Type YES>")
if confirm != "YES":
    print "abort!"
    sys.exit(-1) 

start_id = 1
if len(sys.argv) == 2:
    start_id = int(sys.argv[1])
else:
    print "Usage: %s <start_id>" % (sys.argv[0])
    sys.exit(-1)

print "Starting with id %d" % start_id

red = s.ConstantColor(Color(255, 0, 0))
red.chain(f.Brightness(g.Sin(.25)))

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)

id = start_id
while True:
    inp = raw_input("Hit enter to program node %d" % id)
    if inp.startswith("q"):
        break

    ch.clear_ids()
    ch.set_id(id)
    ch.set_classes([[id]])
    ch.send_pattern_to_class(0, red)
    ch.next_pattern(id, 0)
    sleep(1)
    ch.off(id)
    id += 1

print "done"
