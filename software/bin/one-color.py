#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from hippietrap.geometry import HippieTrapGeometry
from time import sleep, time

if len(sys.argv) != 4:
    print "Usage: %s red green blue" % sys.argv[0]
    sys.exit(-1)

with HippieTrap() as ch:
    ch.set_color(BROADCAST, Color(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))
