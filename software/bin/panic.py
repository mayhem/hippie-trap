#!/usr/bin/python

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time


device = "/dev/serial0"

ch = HippieTrap()
ch.open(device)
ch.send_panic()
