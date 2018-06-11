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

def dim_color_with_arc_distance(angle0, angle1, color):
    delta = math.fabs(angle0 - angle1)
    dim = max(0.0, 1.0 - (delta / 15))
    return Color(color.red * dim, color.green * dim, color.blue * dim)

geo = HippieTrapGeometry()

with HippieTrap() as ch:
    try:
        fb = FrameBuffer(ch)
        while True:
            dt = datetime.datetime.now()
            print dt

            # calculate seconds
            t = float(dt.second) + (float(dt.microsecond) / 1000000)
            angle = (t / 60.0) * 180

            bottles = geo.get_near_bottles_for_ring(1, angle, 10)
            for index, bottle_angle in bottles:
                fb.set_color(index, dim_color_with_arc_distance(angle, bottle_angle, Color(128, 30, 0)))


            # calculate minutes
            angle = (float(dt.minute) / 60.0) * 180

            bottles = geo.get_near_bottles_for_ring(1, angle, 10)
            for index, bottle_angle in bottles:
                colors = fb.get_color(index)
                for i in range(4):
                    colors[i] += dim_color_with_arc_distance(angle, bottle_angle, Color(128, 0, 128))

                fb.set_color(index, colors)


            # calculate hours
            angle = (float(dt.hour) / 24.0) * 180

            bottles = geo.get_near_bottles_for_ring(0, angle, 10)
            for inde, bottle_angle in bottles:
                fb.set_color(index, dim_color_with_arc_distance(angle, bottle_angle, Color(0, 0, 255)))

            fb.apply()
            fb.clear()
            sleep(1)

    except KeyboardInterrupt:
        ch.clear_cruft()
        ch.clear_cruft()
        for bottle, angle in geo.enumerate_all_bottles():
            ch.set_color(bottle, Color(0,0,0))
            sleep(.02)
