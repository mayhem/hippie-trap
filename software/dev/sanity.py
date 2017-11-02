#!/usr/bin/python

import os
import sys
import math
from hippietrap.chandelier import Chandelier, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time

device = "/dev/serial0"

ch = Chandelier()
ch.open(device)
ch.set_color(BROADCAST, Color(255,0,255))
