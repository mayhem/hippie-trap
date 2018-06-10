#!/usr/bin/python

import os
import sys
import math
import datetime
from colorsys import hsv_to_rgb
from random import random
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES, NUM_RINGS
from hippietrap.color import Color, ColorGenerator
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.framebuffer import FrameBuffer
from time import sleep, time

geo = HippieTrapGeometry()

with HippieTrap() as ch:
try:
    fb = FrameBuffer(ch)
    while True:
        dt = datetime.datetime.now()
        t = float(dt.second) + (float(dt.microsecond) / 1000000)
        angle = (t / 60.0) * 180

        bottles = geo.get_near_bottles(angle, 10)
        for bottle in bottles:
            fb.set_color(bottle[0], Color(255, 60, 0))

        fb.apply()
        sleep(.050)

    except KeyboardInterrupt:
        ch.clear_cruft()
        ch.clear_cruft()
        for bottle, angle in geo.enumerate_all_bottles():
            ch.set_color(bottle, Color(0,0,0))
            sleep(.02)
