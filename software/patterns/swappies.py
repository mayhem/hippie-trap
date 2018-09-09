#!/usr/bin/python

import os
import sys
import math
import random
import abc
from threading import Thread
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color, random_color
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time
from hippietrap.transition import transition_drop_out

class Pattern(PatternBase):

    DELAY = .50
    name = "swappies"

    def flip(self, col1, col2):
        self.trap.send_fade(BROADCAST, 250, (col1, col2, col1, col2))
        self.trap.start_pattern(BROADCAST)
        sleep(self.DELAY)

        self.trap.send_fade(BROADCAST, 250, (col2, col1, col2, col1))
        self.trap.start_pattern(BROADCAST)
        sleep(self.DELAY)

        if self.stop_thread:
            return True

        return False

    def pattern(self):

        while True:
            col1 = random_color()

            col2 = random_color()
            if self.flip(col1, col2):
                break

            col2 = Color(255, 255, 0)
            col2 = random_color()
            if self.flip(col1, col2):
                break

            col2 = Color(0, 255, 0)
            col2 = random_color()
            if self.flip(col1, col2):
                break

            col2 = Color(0, 255, 255)
            col2 = random_color()
            if self.flip(col1, col2):
                break

            col2 = Color(0, 0, 255)
            col2 = random_color()
            if self.flip(col1, col2):
                break

            col2 = Color(255, 0, 255)
            col2 = random_color()
            if self.flip(col1, col2):
                break


if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        run_pattern(trap, Pattern)
