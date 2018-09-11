#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.chandelier import Chandelier, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time

device = "/dev/serial0"

ch = Chandelier()
ch.open(device)
ch.clear_ids()
