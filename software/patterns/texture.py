#!/usr/bin/env python3

import os
import sys
import math
from colorsys import hsv_to_rgb
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time
from random import random
from hippietrap.geometry import HippieTrapGeometry
from hippietrap.color import Color

geo = HippieTrapGeometry()

class TexturePattern(PatternBase):

    PERIOD = 850 
    name = "texture"

    def __init__(self, trap):
        super(PatternBase, self).__init__()
        self.trap = trap
        self.z_factor = .02
        self.xy_factor = .01

    def circle (self, x, y):
        return (int)(self.z_factor * (x * x + y * y))

    def circle2 (self, x, y):
        return (int)(self.z_factor * (3 * x * x + y * y))

    def anticircle (self, x, y):
        return (int)(self.z_factor * (x * x - y * y))

    def xyfun (self, x, y):
        return (int)(self.z_factor * (x * x + self.xy_factor * x * y + y * y))

    def x3y3 (self, x, y):
        return (int)(self.z_factor * (x * x * x + y * y * y))

    def x4y4 (self, x, y):
        return (int)(self.z_factor * (x * x * x * x + y * y * y * y))

    def x3y3_xy (self, x, y):
        try:
            return (int)(self.z_factor * (x * x * x + y * y * y) / (x * y))
        except:
            return 0

    def pattern(self):

        bottles = geo.calculate_bottle_locations()
        self.trap.send_entropy()

        scale = 0
        while True:
            for bottle, coord in enumerate(bottles):
                z = self.circle(coord[0], coord[1])
                y = self.circle2(coord[0], coord[1])
                self.trap.set_color(bottle + 1, Color(z % 255, 0 , y % 255))

            if self.stop_thread:
                break 

            scale += .01
            self.z_factor += .0005
