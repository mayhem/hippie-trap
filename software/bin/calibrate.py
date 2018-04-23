#!/usr/bin/python

import os
import sys
import math
from hippietrap.hippietrap import HippieTrap, BROADCAST
from time import sleep, time

device = "/dev/serial0"

ch = HippieTrap()
ch.open(device)
ch.clear(BROADCAST)
ch.clear(BROADCAST)
ch.calibrate_timers(BROADCAST)

print "Calibration is complete."
