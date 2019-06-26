#!/usr/bin/python

import os
from time import sleep
from hippietrap.hippietrap import HippieTrap, BROADCAST

with HippieTrap() as ch:
    ch.clear(BROADCAST)
    sleep(.1)
    ch.power_off()
