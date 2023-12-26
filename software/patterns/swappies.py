import os
import sys
import math
import random
import abc
from threading import Thread
from hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.color import Color, SystemColors
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time


class SwappiesPattern(PatternBase):

    DELAY = 1.2
    FADE_DURATION = 1000
    name = "swappies"

    def __init__(self, trap):
        PatternBase.__init__(self, trap)
        self.colors = SystemColors()

    def flip(self, col1, col2):
        self.trap.send_fade(ALL, self.FADE_DURATION, (col1, col2, col1, col2))
        self.trap.start_pattern(ALL)
        sleep(self.DELAY)

        self.trap.send_fade(ALL, self.FADE_DURATION, (col2, col1, col2, col1))
        self.trap.start_pattern(ALL)
        sleep(self.DELAY)

        if self.stop_thread:
            return True

        return False

    def pattern(self):

        while True:
            col1 = self.colors.random_color()

            col2 = self.colors.random_color()
            if self.flip(col1, col2):
                break

            col2 = self.colors.random_color()
            if self.flip(col1, col2):
                break

            col2 = self.colors.random_color()
            if self.flip(col1, col2):
                break

            col2 = self.colors.random_color()
            if self.flip(col1, col2):
                break

            col2 = self.colors.random_color()
            if self.flip(col1, col2):
                break

            col2 = self.colors.random_color()
            if self.flip(col1, col2):
                break

        self.trap.stop_pattern(ALL)
