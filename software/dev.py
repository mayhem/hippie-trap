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

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)
ch.send_entropy()

random.seed()
period_s = 1

def pfs(seconds):
    return (math.pi * 2) / seconds

# Debugged patterns

# Wobble: Sin, Random Color Seq, Local Random, Brightness
wobble = function.RandomColorSequence(generator.LocalRandomValue(1.0, 1.50), generator.LocalRandomValue(0.0, 1.00))
wobble.chain(filter.Brightness(generator.Sin(generator.RepeatLocalRandomValue(0))))

# Green saw: sawtooth, Brightness, constant color
green = function.ConstantColor(Color(0,255,0))
green.chain(filter.Brightness(generator.Sawtooth(2)))

# Rainbow, sawtooth, filter
rainbow = function.Rainbow(generator.Sawtooth(3))
rainbow.chain(filter.FadeIn(1))

# Blinking random color
sq = function.RandomColorSequence(generator.LocalRandomValue(1.0, 1.50), generator.LocalRandomValue(0.0, 1.00))
sq.chain(filter.Brightness(generator.Square(.5)))

# Rainbow/white, HSV, local randoms
hsv = function.HSV(generator.Sawtooth(3), generator.Sin(generator.LocalRandomValue(.25, .99)), generator.LocalRandomValue(.25, .99))

# fadein, fade out, constant color
purple = function.ConstantColor(Color(255, 0, 255))
purple.chain(filter.FadeIn(1.0))
purple.chain(filter.FadeOut(1.0, 5.0))

# constant random color
#src = function.ConstantRandomColor(generator.LocalRandomValue(.25, .75), 
#                                   generator.LocalRandomValue(.25, .5),
#                                   generator.LocalRandomValue(.25, .5))

# to test:
# step, square, abs, constant

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

#dist = .15
#base = Color(255, 0, 64)
#while True:
#    triad = function.CompColorSource(base, dist, 0)
#    print triad[0]
#    ch.set_color(BROADCAST, triad[0])
#    sleep(1)
#
#    triad = function.CompColorSource(base, dist, 1)
#    print triad[0]
#    ch.set_color(BROADCAST, triad[0])
#    sleep(1)

#    triad = function.CompColorSource(base, dist, 2)
#    print triad[0]
#    ch.set_color(BROADCAST, triad[0])
#    sleep(1)

# this python crashes
#hsv = function.HSV(generator.Sawtooth(.15), generator.Sin(generator.LocalRandomValue(.25, .99)), generator.Constant(generator.LocalRandomValue(.25, .99)))


hsv = function.HSV(generator.Sawtooth(3), generator.Sin(3))
green = function.ConstantColor(Color(0,255,0))
green.chain(filter.Brightness(generator.Sawtooth(1)))

src = sq

if len(sys.argv) == 2:
    local = int(sys.argv[1])
else:
    local = 0

if local:
    print "running local"
    ch.run(src, DELAY, 0)
else:
    print "Sending %d bytes." % len(src.describe())
    ch.send_pattern(BROADCAST, src) 
    ch.next_pattern(BROADCAST, 0)
    ch.debug_serial(0)
