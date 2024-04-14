#!/usr/bin/env python3

import os
import sys
import math
from hippietrap import HippieTrap, BROADCAST
from time import sleep, time

with HippieTrap() as ch:
    ch.begin()
    ch.clear(BROADCAST)
    ch.clear(BROADCAST)
    ch.calibrate_timers(BROADCAST)

    print("Calibration is complete.")
