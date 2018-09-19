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
from hippietrap.geometry import HippieTrapGeometry
from time import sleep, time

geo = HippieTrapGeometry()

if len(sys.argv) == 2:
    brightness = int(sys.argv[1])
else:
    brightness = 100


def transition_drop_out(trap):
    bottles = [ i for i in range(1, NUM_NODES + 1) ]
    random.shuffle(bottles)
    for bottle in bottles:
        trap.clear(bottle)
        sleep(.01)

def transition_sweep_clear(trap):
    for bottle, angle in geo.enumerate_all_bottles():
        trap.set_color(bottle, Color(0,0,0))
        sleep(.02)

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

    ret = []
    for p in patterns:
        mod = importlib.import_module("hippietrap.patterns.%s" % p)
        ret.append(mod.Pattern)

    return ret


def main(transitions = True):

    with HippieTrap() as trap:
        trap.begin()
        trap.set_brightness(ALL, brightness)

        patterns = load_patterns("../patterns")

        while True:
            random.shuffle(patterns)
            for pattern_class in patterns:
                pattern = pattern_class(trap)
                print pattern.name
                pattern.start()
                try:
                    sleep(10)
                except KeyboardInterrupt:
                    pattern.stop()
                    pattern.join()
                    trap.clear(ALL)
                    return

                pattern.stop(transition=transitions)
                pattern.join()


if __name__ == "__main__":
    main()
