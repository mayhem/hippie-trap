#!/usr/bin/python

import os
import sys
import math
from random import randint
from time import sleep, time

from hippietrap.chandelier import Chandelier, BROADCAST
from hippietrap.function import Pattern, Function
from hippietrap.color import Color
import hippietrap.common as common

DELAY = .02

device = "/dev/serial0"

ch = Chandelier()
ch.open(device)
#ch.clear(BROADCAST)
#ch.send_entropy()
#ch.set_brightness(BROADCAST, 100)

# TODO: Sending to the same dest does not have the expected result
p = Pattern(10,
        Function(common.FUNC_SQUARE, common.DEST_ALL_RED, 1.0, 0.0, 1.0, 0.0, .6),
        Function(common.FUNC_SQUARE, common.DEST_ALL_BLUE, .8, 0.0, 1.0, 0.0, .5),
        Function(common.FUNC_SQUARE, common.DEST_ALL_GREEN, .6, 0.0, 1.0, 0.0, .4)
)

try:
    print "send one"
    ch.send_pattern(BROADCAST, p)
    ch.start_pattern(BROADCAST)

    while False:
        print "start one"
        sleep(3)
        break

        print "send two"
        ch.send_pattern(2, p2)

        print "start two"
        ch.start_pattern(2)
        sleep(3)

        print "send three"
        ch.send_pattern(2, p3)

        print "start three"
        ch.start_pattern(2)
        sleep(3)

        print "send one"
        ch.send_pattern(2, p1)

except KeyboardInterrupt:
    ch.off(BROADCAST)
