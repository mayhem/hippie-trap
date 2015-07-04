#!/usr/bin/python

from chandelier import Chandelier, BROADCAST
import function as src
import generator as g
import filter as f 
import random

wobble = src.RandomColorSequence(g.LocalRandomValue(1.0, 2.0), g.LocalRandomValue(0.0, 1.00))
wobble.chain(f.Brightness(g.Sin(g.RepeatLocalRandomValue(0))))

rainbow = src.HSV(g.Sawtooth(6, g.LocalRandomValue(0.0, 1.0)))

wrainbow = src.HSV(g.Sawtooth(6), g.Sin(g.LocalRandomValue(.25, .99)), g.LocalRandomValue(.25, .99))

rgb = src.RGBSource(g.Sawtooth(1), g.Constant(1), g.Sin(1))

comp = src.CompColorSource(src.HSV(g.Sawtooth(8)), g.Sin(3, 0, .1), 1)

const_rand = src.ConstantRandomColor(g.LocalRandomValue(0, 1.0),
                                          g.LocalRandomValue(.55, .9),
                                          g.LocalRandomValue(.55, .9))
const_rand.chain(f.Brightness(g.Sin(3, 0, .2, .8)))

xyz = src.XYZSource(g.Sawtooth(3, 0, 1, 1), 
                     g.Constant(0), 
                     src.XYZ_HSV, 
                     g.Sin(1),
                     g.Constant(.8), 
                     g.Constant(.8))

pattern_set = [
    (wobble, 30, "wobble"),
    (xyz, 30, "xyz"),
    (const_rand, 15, "const rand"),
    (rainbow, 15, "rainbow"),
    (rgb, 30, "rgb"),
    (wrainbow, 3, "wrainbow"), 
    (comp, 30, "comp"),
]
