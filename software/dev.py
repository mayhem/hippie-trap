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
ch.set_brightness(BROADCAST, 100)

random.seed()
period_s = 1

def pfs(seconds):
    return (math.pi * 2) / seconds

# Debugged patterns

# Wobble: Sin, Random Color Seq, Local Random, Brightness
wobble = function.RandomColorSequence(generator.LocalRandomValue(.5, .75), generator.LocalRandomValue(0.0, 1.00))
wobble.chain(filter.Brightness(generator.Sin(generator.RepeatLocalRandomValue(0))))

# Green saw: sawtooth, Brightness, constant color
green = function.ConstantColor(Color(0,255,0))
green.chain(filter.Brightness(generator.Sawtooth(1)))

# Rainbow, sawtooth, filter
rainbow = function.Rainbow(generator.Sawtooth(3))
rainbow.chain(filter.FadeIn(1))

# Blinking random color
sq = function.RandomColorSequence(generator.LocalRandomValue(1.0, 1.50), generator.LocalRandomValue(0.0, 1.00))
sq.chain(filter.Brightness(generator.Square(.5)))

# Rainbow/white, HSV, local randoms
hsv = function.HSV(generator.Sawtooth(6), generator.Sin(generator.LocalRandomValue(.25, .99)), generator.LocalRandomValue(.25, .99))

# fadein, fade out, constant color
purple = function.ConstantColor(Color(255, 0, 255))
purple.chain(filter.FadeIn(.5))
purple.chain(filter.FadeOut(.5, 1.5))

# Impulse
imp = function.ConstantColor(Color(255,0,0))
imp.chain(filter.Brightness(generator.Impulse(1)))

# Step
step = function.ConstantColor(Color(0,0,255))
step.chain(filter.Brightness(generator.Step(1, -1)))

# RGBColor Source
rgb = function.RGBSource(generator.Sawtooth(1), generator.Constant(1), generator.Sin(1))

# ColorShift
color_shift = function.ConstantColor(Color(255,0,0))
color_shift.chain(filter.ColorShift(.6, 0, 0))

# Comp color source
comp = function.CompColorSource(function.HSV(generator.Sawtooth(2)), generator.Sin(1, 0, .1), 1)

# constant random color
const_rand = function.ConstantRandomColor(generator.LocalRandomValue(0, 1.0), 
                                   generator.LocalRandomValue(.25, .5),
                                   generator.LocalRandomValue(.25, .5))

# SrcOp
red = function.ConstantColor(Color(255,0,0))
red.chain(filter.Brightness(generator.Square(1)))
grn = function.ConstantColor(Color(0,255,0))
grn.chain(filter.Brightness(generator.Square(1, -.5)))
blu = function.ConstantColor(Color(0,0,255))
blu.chain(filter.Brightness(generator.Square(.5)))
srcop = function.SourceOp(common.OP_ADD, red, grn, blu)
srcop.chain(filter.Brightness(generator.Constant(.75)))

# this python crashes
hsv = function.HSV(generator.Sawtooth(.15), generator.Sin(generator.LocalRandomValue(.25, .99)), generator.Constant(generator.LocalRandomValue(.25, .99)))

function.set_position(.5, .5, 0)
ch.set_position(1, .5, .5, 0)
xyz = function.XYZSource(generator.Constant(2), generator.Sawtooth(1), function.XYZ_RGB, generator.Step(1), generator.Step(1))
src = wobble

pattern_set = [(wobble, 5), (green, 3), (rainbow, 4), (purple, 2), (imp, 2), (step, 2), (const_rand, 2), (rgb, 3), (color_shift, 2), (srcop, 4), (comp, 4)]

red = function.ConstantColor(Color(255,0,0))
blue = function.ConstantColor(Color(0,0,255))
fade_test = [ (red, 2), (blue, 2)]

local = 0
test = 0
for arg in sys.argv[1:]:
    if arg.startswith("lo"):
        local = 1
    if arg.startswith("te"):
        test = 1
    if arg.startswith("fa"):
        pattern_set = fade_test

if local:
    print "running local"
    ch.run(src, DELAY, 0)
elif test:
    ch.send_pattern(BROADCAST, purple)
    ch.next_pattern(BROADCAST, 0)
    ch.debug_serial(1)
    while True:
        for pattern, duration in pattern_set:
            ch.send_pattern(BROADCAST, pattern) 
            ch.next_pattern(BROADCAST, 500)
            ch.debug_serial(duration)
        
else:
    print "Sending %d bytes." % len(src.describe())
    ch.send_pattern(BROADCAST, src) 
    ch.next_pattern(BROADCAST, 0)
    ch.debug_serial(0)
