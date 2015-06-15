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

INC = .1
period_s = 1

ch = Chandelier()

src1 = function.ConstantColor(Color(255,0,0))
src1.chain(filter.Brightness(generator.Sin((math.pi * 2) / period_s, -math.pi/2, .5, .5)))

src2 = function.ConstantColor(Color(0,0,255))
src2.chain(filter.Brightness(generator.Sin((math.pi * 2) / period_s, 0, .5, .5)))

op = function.SourceOp(common.OP_ADD, src1, src2)

print "len: %d" % len(op.describe())

t = 0
while t < math.pi:
    print t, src1[t], src2[t], op[t]
    t += INC
