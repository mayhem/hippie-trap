#!/usr/bin/env python3

import os
import sys
import math
import _thread
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color
from time import sleep, time

trap = None

def send_panic():
    trap.send_panic()

with HippieTrap() as ch:
    trap = ch

    print("setup hippie trap")
    ch.begin()
    sleep(1)

    print("power off")
    ch.power_off()
    sleep(1)

    print("send panic")
    _thread.start_new_thread(send_panic, ())
    sleep(1)

    print("power on")
    ch.power_on()
    sleep(5)

    print("done. hopefully it did the trick!")
