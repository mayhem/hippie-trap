#!/usr/bin/python

import abc
import os
import sys
from threading import Thread
from time import sleep, time
from hippietrap import ALL

def run_pattern(ch, pattern, clear=False):
    r = pattern(ch)
    r.start()
    try:
        while True:
            sleep(100)
    except KeyboardInterrupt:
        print "stopping ..."

        if clear:
            ch.clear_cruft()
            ch.clear_cruft()

        ch.stop_pattern(ALL)

        r.stop()
        r.join()
        print 


class PatternBase(Thread):

    def __init__(self, trap):
        Thread.__init__(self)
        self.trap = trap
        self.stop_thread = False
        self.transition = False

    def stop(self, transition = True):
        self.stop_thread = True
        self.transition = transition

    @abc.abstractmethod
    def pattern(self):
        pass


    def run(self):
        while not self.stop_thread:
            self.pattern()

        sleep(.1)

