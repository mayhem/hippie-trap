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

confirm = raw_input("Are you sure you want to clear all ids? Type YES>")
if confirm == "YES":
    ch = Chandelier()
    ch.open(device)
    ch.off(BROADCAST)
    ch.clear_ids()
    print "ids cleared"
else:
    print "aborted"
