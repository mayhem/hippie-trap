#!/usr/bin/python
import abc
import math
import colorsys
import generators

# Generator -> Sawtooth, Sine, Cos, Square, Hilbert, Impulse
# ColorSource -> given t: get color
# Filter -> given t, color: return color

#Generator(args)
#ColorSource(Generator, args)
#Filter(Time

class Color(object):

    def __init__(self, r, g, b):
        self.color = [r, g, b]

    def __str__(self):
        return "Color(%d,%d,%d)" % (self.color[0], self.color[1], self.color[2])

    @abc.abstractmethod
    def __getitem__(self, i):
        return self.color[i]

class ColorSource(object):

    def __init__(self, generator):
        self.g = generator

    @abc.abstractmethod
    def __getitem__(self, t):
        pass

class ColorWheel(ColorSource):

    def __init__(self, period = 1.0, phase = 0.0, generator = None):
        if generator:
            g = generator
        else:
            print period, phase
            g = generators.Sawtooth(period, phase)
        super(Rainbow, self).__init__(g)

    def __getitem__(self, t):
        col = colorsys.hsv_to_rgb(self.g[t], 1, 1)
        return Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255))

class Rainbow(ColorSource):

    def __init__(self, period = 1.0, phase = 0.0, generator = None):
        if generator:
            g = generator
        else:
            print period, phase
            g = generators.Sawtooth(period, phase)
        super(Rainbow, self).__init__(g)

    def __getitem__(self, t):
        color = [0,0,0]

        wheel_pos = 255 - int(255 * self.g[t])
        if wheel_pos < 85:
            color[0] = int(255 - wheel_pos * 3)
            color[1] = 0
            color[2] = int(wheel_pos * 3)
        elif wheel_pos < 170:
            wheel_pos -= 85
            color[0] = 0
            color[1] = int(wheel_pos * 3)
            color[2] = 255 - int(wheel_pos * 3)
        else:
            wheel_pos -= 170
            color[0] = int(wheel_pos * 3)
            color[1] = 255 - int(wheel_pos * 3)
            color[2] = 0

        return Color(color[0], color[1], color[2])
