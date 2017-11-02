#!/usr/bin/python

import os
import sys
import math
from hippietrap.chandelier import Chandelier, BROADCAST
from time import sleep, time

device = "/dev/serial0"

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)
ch.calibrate_timers(BROADCAST)

print "Calibration is complete."
