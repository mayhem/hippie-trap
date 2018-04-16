#!/usr/bin/python

import os
import sys
import math
from hippietrap.chandelier import Chandelier, BROADCAST

device = "/dev/serial0"
if len(sys.argv) == 2:
    device = sys.argv[1]

ch = Chandelier()
ch.open(device)
ch.clear(BROADCAST)
ch.clear(BROADCAST)
ch.enter_bootloader(BROADCAST)
