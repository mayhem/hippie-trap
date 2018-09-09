#!/usr/bin/python

import abc
import os
import sys
from threading import Thread
from time import sleep, time

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

        r.stop()
        r.join()
        print 


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


