#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST
import function
import generator
import filter
import random
import common
from time import sleep, time
from color import Color

DELAY = .02

device = "/dev/ttyAMA0"
if len(sys.argv) == 2:
    device = sys.argv[1]

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)
ch.send_entropy()

random.seed()
period_s = 1

#hsv = function.HSV(generator.Sawtooth(.15))
#
#rainbow = function.Rainbow(generator.Sawtooth(.15))
##rainbow.chain(filter.FadeIn(1))
##rainbow.chain(filter.FadeOut(1.0, 5.0))
#
#green = function.ConstantColor(Color(255, 0, 0))
##green.chain(filter.FadeIn(1.0))
#
#purple = function.ConstantColor(Color(0, 0, 255))
##purple.chain(filter.FadeIn(1.0))
##purple.chain(filter.FadeOut(1.0, 5.0))

wobble = function.RandomColorSequence(period_s, random.randint(0, 255))
g = generator.Sin((math.pi * 2) / period_s, -math.pi/2, .5, .5)
g = generator.Sparkle()
wobble.chain(filter.Brightness(g))

#src1 = function.ConstantColor(Color(255,0,0))
#src1.chain(filter.Brightness(generator.Sin((math.pi * 3) / period_s, 2, .5, .5)))
#
#src2 = function.ConstantColor(Color(0,0,255))
#src2.chain(filter.Brightness(generator.Sin((math.pi * 2) / period_s, 1, .5, .5)))
#
#src3 = function.ConstantColor(Color(0,255,0))
#src3.chain(filter.Brightness(generator.Sin(math.pi / period_s, 1, .5, .5)))
#
#op = function.SourceOp(common.OP_ADD, src1, src2, src3)

dist = .15
base = Color(255, 0, 64)
while True:
    triad = function.CompColorSource(base, dist, 0)
    print triad[0]
    ch.set_color(BROADCAST, triad[0])
    sleep(1)

    triad = function.CompColorSource(base, dist, 1)
    print triad[0]
    ch.set_color(BROADCAST, triad[0])
    sleep(1)

    triad = function.CompColorSource(base, dist, 2)
    print triad[0]
    ch.set_color(BROADCAST, triad[0])
    sleep(1)

#ch.run(op, DELAY, 20)
