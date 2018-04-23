#!/usr/bin/python

import os
import sys
import math
from hippietrap.hippietrap import HippieTrap, BROADCAST

device = "/dev/serial0"
if len(sys.argv) == 2:
    device = sys.argv[1]

ch = HippieTrap()
ch.open(device)
ch.clear(BROADCAST)
