#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST, NUM_NODES
import function as s
import generator as g
import filter as f
import random as r
import common as com
from time import sleep, time
from color import Color

device = "/dev/ttyAMA0"

r.seed()

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)
ch.send_entropy()
ch.set_brightness(BROADCAST, 100)
for p in range(1, NUM_NODES + 1):
    ch.set_position(p, r.random(), r.random(), 0)

ch.set_classes([range(1,12), [12]])

# outer ring
for i in range(1, 12):
    angle = i / 11.0
    ch.set_angle(i, angle)

def circular_random_colors(ch):
    white = s.ConstantColor(Color(255, 255, 255))
    white.chain(f.Brightness(g.Sin(2, 0, .2, .6)))

    radial = s.RandomColorSequence(g.LocalRandomValue(1.0, 1.50), g.LocalRandomValue(0.0, 1.00))
    radial.chain(f.Brightness(g.Sin(1, g.LocalAngle())))

    ch.send_pattern_to_class(0, radial) 
    ch.send_pattern_to_class(1, white) 
    ch.next_pattern(BROADCAST, 200)

def circular_rainbow(ch):
    white = s.ConstantColor(Color(255, 255, 255))
    white.chain(f.Brightness(g.Sin(2, 0, .2, .6)))

    radial = s.HSV(g.Sawtooth(5))
    radial.chain(f.Brightness(g.Sin(1, g.LocalAngle())))

    ch.send_pattern_to_class(0, radial) 
    ch.send_pattern_to_class(1, white) 
    ch.next_pattern(BROADCAST, 200)

def wobble(ch):
    wobble = s.RandomColorSequence(g.LocalRandomValue(1.0, 2.0), g.LocalRandomValue(0.0, 1.00))
    wobble.chain(f.Brightness(g.Sin(g.RepeatLocalRandomValue(0))))
    ch.send_pattern(BROADCAST, wobble) 
    ch.next_pattern(BROADCAST, 200)

def rainbow(ch):
    rainbow = s.HSV(g.Sawtooth(6, g.LocalRandomValue(0.0, 1.0)))
    ch.send_pattern(BROADCAST, rainbow) 
    ch.next_pattern(BROADCAST, 200)

def xyz(ch):
    xyz = s.XYZSource(g.Sawtooth(3, 0, 1, 1),
            g.Constant(0),
            s.XYZ_HSV,
            g.Sin(1),
            g.Constant(.8),
            g.Constant(.8))
    ch.send_pattern(BROADCAST, xyz) 
    ch.next_pattern(BROADCAST, 200)

def cool(ch):
    pat = s.HSV(g.Sawtooth(6), g.Sin(g.LocalRandomValue(.25, .99)), g.LocalRandomValue(.25, .99))
    ch.send_pattern(BROADCAST, pat) 
    ch.next_pattern(BROADCAST, 200)

def test(ch):
    pat = s.RGBSource(g.Sawtooth(1), g.Constant(1), g.Sin(1))
    ch.send_pattern(BROADCAST, pat) 
    ch.next_pattern(BROADCAST, 200)

while True:
    cool(ch);
    sleep(15)
    xyz(ch)
    sleep(5)
    rainbow(ch)
    sleep(5)
    circular_random_colors(ch)
    sleep(5)
    wobble(ch)
    sleep(5)
    circular_rainbow(ch)
    sleep(5)
