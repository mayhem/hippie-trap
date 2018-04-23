#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time
from random import random

STEPS = 5000

device = "/dev/serial0"

ch = HippieTrap()
ch.open(device)
ch.clear(BROADCAST)

ch.set_color(BROADCAST, Color(0, 0, 0))

print "to red"
ch.send_fade(BROADCAST, 3000, (Color(255, 0, 0), ))
ch.start_pattern(BROADCAST)
sleep(3)
ch.stop_pattern(BROADCAST)

print "to green"
ch.send_fade(BROADCAST, 3000, (Color(0, 255, 0), ))
ch.start_pattern(BROADCAST)
sleep(3)
ch.stop_pattern(BROADCAST)

print "to blue"
ch.send_fade(BROADCAST, 3000, (Color(0, 0, 255), ))
ch.start_pattern(BROADCAST)
sleep(3)
ch.stop_pattern(BROADCAST)

print "to off"
ch.send_fade(BROADCAST, 3000, (Color(10, 0, 0), ))
ch.start_pattern(BROADCAST)
sleep(3)
ch.stop_pattern(BROADCAST)
