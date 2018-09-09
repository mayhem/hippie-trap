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

class Pattern(PatternBase):

    DELAY = .50

    def flip(self, col1, col2):
        self.trap.send_fade(BROADCAST, 250, (col1, col2, col1, col2))
        self.trap.start_pattern(BROADCAST)
        sleep(self.DELAY)

        self.trap.send_fade(BROADCAST, 250, (col2, col1, col2, col1))
        self.trap.start_pattern(BROADCAST)
        sleep(self.DELAY)

    def pattern(self):

        col1 = random_color()

        col2 = random_color()
        self.flip(col1, col2)
        if self.stop_thread: 
            return

        col2 = Color(255, 255, 0)
        col2 = random_color()
        self.flip(col1, col2)
        if self.stop_thread: 
            return

        col2 = Color(0, 255, 0)
        col2 = random_color()
        self.flip(col1, col2)
        if self.stop_thread: 
            return

        col2 = Color(0, 255, 255)
        col2 = random_color()
        self.flip(col1, col2)
        if self.stop_thread: 
            return

        col2 = Color(0, 0, 255)
        col2 = random_color()
        self.flip(col1, col2)
        if self.stop_thread: 
            return

        col2 = Color(255, 0, 255)
        col2 = random_color()
        self.flip(col1, col2)


if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        run_pattern(trap, Pattern)

        bottles = [ i for i in range(1, NUM_NODES + 1) ]
        random.shuffle(bottles)
        for bottle in bottles:
            trap.clear(bottle)
            sleep(.01)
