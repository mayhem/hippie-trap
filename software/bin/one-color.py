#!/usr/bin/env python3

import os
import sys
import math
from colorsys import hsv_to_rgb
from random import random
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from hippietrap.geometry import HippieTrapGeometry
from time import sleep, time

col = Color(255, 210, 70)
if len(sys.argv) == 4:
    col = Color(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

with HippieTrap() as ch:
    ch.begin()
    ch.set_color(BROADCAST, col)
