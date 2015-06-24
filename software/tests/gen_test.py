#!/usr/bin/python

import os
import sys
import math
from chandelier import Chandelier, BROADCAST
import function
import generator
import filter
import random
from time import sleep, time
from color import Color

g = generator.Abs(generator.Line())
g = generator.Line(1,0,1, -1)
for i in xrange(200):
    t = i - 100
    print "%d %.4f" % (t, g[t])
