#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST, NUM_NODES
import function
import generator
import random
import common
from time import sleep, time
from color import Color

device = "/dev/serial0"

ch = Chandelier()
ch.open(device)
ch.set_color(BROADCAST, Color(255,0,255))
