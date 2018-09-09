#!/usr/bin/python

import os
import sys
import math
import random
import abc
import importlib
from threading import Thread
from hippietrap.hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.color import Color, random_color
from hippietrap.pattern import PatternBase, run_pattern
from time import sleep, time

def transition_1(trap):
    bottles = [ i for i in range(1, NUM_NODES + 1) ]
    random.shuffle(bottles)
    for bottle in bottles:
        trap.clear(bottle)
        sleep(.01)


def load_patterns(path):

    try:
        files = os.listdir(path)
    except IOError as err:
        print "Cannot open patterns dir '%s'" % path
        return []

    patterns = []
    for f in files:
        if f.endswith(".py") and not f.startswith("__"):
            patterns.append(f[:-3])

    print patterns

    ret = []
    for p in patterns:
        mod = importlib.import_module("hippietrap.patterns.%s" % p)
        ret.append(mod.Pattern)

    return ret


def main():

    with HippieTrap() as trap:
        try:
            trap.begin()

            patterns = load_patterns("../patterns")

            while True:
                random.shuffle(patterns)
                for pattern_class in patterns:
                    pattern = pattern_class(trap)
                    pattern.start()
                    sleep(15)
                    pattern.stop()
                    pattern.join()

                    transition_1(trap)

        except KeyboardInterrupt:
            trap.clear(ALL)


if __name__ == "__main__":
    main()
