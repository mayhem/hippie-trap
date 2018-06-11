#!/usr/bin/python

import os
import sys
import math
import random
import abc
from threading import Thread
from hippietrap.hippietrap import HippieTrap, BROADCAST, NUM_NODES
from hippietrap.color import Color, random_color
from time import sleep, time

DELAY = .50

class PatternBase(Thread):

    def __init__(self, trap):
        Thread.__init__(self)
        self.trap = trap
        self.stop_thread = False


    def stop(self):
        self.stop_thread = True


    @abc.abstractmethod
    def pattern(self):
        pass


    def run(self):
        while not self.stop_thread:
            self.pattern()

        sleep(.1)


class PatternFlashies(PatternBase):

    def flash(self, ch, col1, col2):
        self.trap.set_color_array(BROADCAST, (col1, col2, col1, col2))
        sleep(DELAY)
        self.trap.set_color_array(BROADCAST, (col2, col1, col2, col1))
        sleep(DELAY)

    def flip(self, ch, col1, col2):
        self.trap.send_fade(BROADCAST, 250, (col1, col2, col1, col2))
        self.trap.start_pattern(BROADCAST)
        sleep(DELAY)

        self.trap.send_fade(BROADCAST, 250, (col2, col1, col2, col1))
        self.trap.start_pattern(BROADCAST)
        sleep(DELAY)

    def pattern(self):

        col1 = random_color()

        col2 = random_color()
        self.flip(ch, col1, col2)
        if self.stop: 
            return

        col2 = Color(255, 255, 0)
        col2 = random_color()
        self.flip(ch, col1, col2)
        if self.stop: 
            return

        col2 = Color(0, 255, 0)
        col2 = random_color()
        self.flip(ch, col1, col2)
        if self.stop: 
            return

        col2 = Color(0, 255, 255)
        col2 = random_color()
        self.flip(ch, col1, col2)
        if self.stop: 
            return

        col2 = Color(0, 0, 255)
        col2 = random_color()
        self.flip(ch, col1, col2)
        if self.stop: 
            return

        col2 = Color(255, 0, 255)
        col2 = random_color()
        self.flip(ch, col1, col2)


if __name__ == "__main__":
    with HippieTrap() as ch:
        r = PatternFlashies(ch)
        r.start()
        try:
            while True:
                sleep(100)
        except KeyboardInterrupt:
            print "[ waiting for pattern to stop ]"
            r.stop()
            r.join()

            bottles = [ i for i in range(1, NUM_NODES + 1) ]
            random.shuffle(bottles)
            print bottles
            for bottle in bottles:
                ch.clear(bottle)
                sleep(.01)
