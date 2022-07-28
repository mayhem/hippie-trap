#!/usr/bin/env python3

import os
import sys
import math
import random

from time import sleep, time
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color

with HippieTrap() as ch:
    ch.begin()

    start = int(sys.argv[1])

    for id in range(start,NUM_NODES+1):
        ch.set_color(id, Color(0,0,0))

    for id in range(start,NUM_NODES+1):
        print(id)
        ch.set_color(id, Color(0,0,255))
        sleep(.5)
