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
        Function(common.FUNC_SQUARE, common.DEST_ALL_RED, .5, 0.0, 1.0, 0.0, .6),
        Function(common.FUNC_SQUARE, common.DEST_ALL_BLUE, .4, 0.0, 1.0, 0.0, .6),
)
p1 = Pattern(10,
        Function(common.FUNC_SQUARE, common.DEST_ALL_RED, 1.0, 0.0, 1.0, 0.0, .6),
        Function(common.FUNC_SQUARE, common.DEST_ALL_BLUE, .8, 0.0, 1.0, 0.0, .5),
        Function(common.FUNC_SQUARE, common.DEST_ALL_GREEN, .6, 0.0, 1.0, 0.0, .4)
)

try:
    print "send pattern"
    ch.send_pattern(BROADCAST, p)
    sleep(.1)

    print "start pattern"
    ch.start_pattern(BROADCAST)

except KeyboardInterrupt:
    ch.off(BROADCAST)
