#!/usr/bin/python

from chandelier import Chandelier, BROADCAST
import function as src
import generator as g
import filter as f 

wobble = src.RandomColorSequence(g.LocalRandomValue(1.0, 2.0), g.LocalRandomValue(0.0, 1.00))
wobble.chain(f.Brightness(g.Sin(g.RepeatLocalRandomValue(0))))

rainbow = src.HSV(g.Sawtooth(6, g.LocalRandomValue(0.0, 1.0)))

wrainbow = src.HSV(g.Sawtooth(6), g.Sin(g.LocalRandomValue(.25, .99)), g.LocalRandomValue(.25, .99))

rgb = src.RGBSource(g.Sawtooth(1), g.Constant(1), g.Sin(1))

pattern_set = [
    (wobble, 10), 
    (rainbow, 10),
    (rgb, 10),
    (wrainbow, 10)
]
