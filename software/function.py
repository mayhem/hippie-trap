#!/usr/bin/python
import abc
import math
import colorsys
import generator
import random
from color import Color, hueToColor
import common

class ColorSource(common.ChainLink):

    def __init__(self, gen, gen2 = None, gen3 = None):
        super(ColorSource, self).__init__()
        self.g = gen
        self.g2 = gen2
        self.g3 = gen3
        self.next = None

    @abc.abstractmethod
    def __getitem__(self, t):
        pass

class ConstantColor(ColorSource):

    def __init__(self, color):
        self.color = color
        super(ConstantColor, self).__init__(None)

    def describe(self):
        desc = common.make_function(common.FUNC_CONSTANT_COLOR, (common.ARG_COLOR,))
        desc += common.pack_color(self.color)
        #print "%s()" % (self.__class__.__name__)
        return desc + self.describe_next()

    def __getitem__(self, t):
        return self.call_next(t, self.color)

class ConstantRandomColor(ColorSource):

    def __init__(self, hue, sat = 1.0, value = 1.0):
        super(ConstantRandomColor, self).__init__(None)
        self.hue = hue
        self.sat = sat
        self.value = value

        if type(self.hue) in (int, float):
            self.hue_f = None
        else:
            self.hue_f = self.hue
            self.hue = self.hue_f[0]

        if type(self.sat) in (int, float):
            self.sat_f = None
        else:
            self.sat_f = self.sat
            self.sat = self.sat_f[0]

        if type(self.value) in (int, float):
            self.value_f = None
        else:
            self.value_f = self.value
            self.value = self.value_f[0]

    def describe(self):
        args = []
        desc = bytearray()

        if self.hue_f:
            desc += self.hue_f.describe()
            args.append(common.ARG_FUNC)
        else:
            desc += common.pack_fixed(self.hue)
            args.append(common.ARG_VALUE)

        if self.sat_f:
            desc += self.sat_f.describe()
            args.append(common.ARG_FUNC)
        else:
            desc += common.pack_fixed(self.sat)
            args.append(common.ARG_VALUE)

        if self.value_f:
            desc += self.value_f.describe()
            args.append(common.ARG_FUNC)
        else:
            desc += common.pack_fixed(self.value)
            args.append(common.ARG_VALUE)

        return common.make_function(common.FUNC_CONSTANT_RANDOM_COLOR, args) + desc + self.describe_next()

    def __getitem__(self, t):
        col = colorsys.hsv_to_rgb(self.hue, self.sat, self.value)
        self.color = Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255))
        return self.call_next(t, self.color)

class RandomColorSequence(ColorSource):
    '''
       Return colors that appear _random_ to a human.
    '''

    def __init__(self, period=1, seed=0):
        super(RandomColorSequence, self).__init__(None)
        self.period = period
        self.seed = seed

        if type(self.period) in (int, float):
            self.period_f = None
        else:
            self.period_f = self.period
            self.period = self.period_f[0]

        if type(self.seed) in (int, float):
            self.seed_f = None
        else:
            self.seed_f = self.seed
            self.seed = self.seed_f[0]

    def describe(self):
        args = []
        desc = bytearray()

        if self.period_f:
            desc += self.period_f.describe()
            args.append(common.ARG_FUNC)
        else:
            desc += common.pack_fixed(self.period)
            args.append(common.ARG_VALUE)

        if self.seed_f:
            desc += self.seed_f.describe()
            args.append(common.ARG_FUNC)
        else:
            desc += common.pack_fixed(self.seed)
            args.append(common.ARG_VALUE)

        return common.make_function(common.FUNC_RAND_COL_SEQ, args) + desc + self.describe_next()

    def __getitem__(self, t):
        random.seed(self.seed + (int)(t / self.period))
        return self.call_next(t, hueToColor(random.random()))

class HSV(ColorSource):

    def __init__(self, gen, g2 = None, g3 = None):
        super(HSV, self).__init__(gen, g2, g3)

    def describe(self):
        if self.g3:
            desc = common.make_function(common.FUNC_HSV, (common.ARG_FUNC, common.ARG_FUNC, common.ARG_FUNC))
        elif self.g2:
            desc = common.make_function(common.FUNC_HSV, (common.ARG_FUNC, common.ARG_FUNC))
        else:
            desc = common.make_function(common.FUNC_HSV, (common.ARG_FUNC,))

        #print "%s(" % (self.__class__.__name__),
        if self.g:
            desc += self.g.describe()
            if self.g2:
                desc += self.g2.describe()
            if self.g3:
                desc += self.g3.describe()
        #print ")"
        return desc + self.describe_next()

    def __getitem__(self, t):
        if self.g2 and self.g3:
            col = colorsys.hsv_to_rgb(self.g[t], self.g2[t], self.g3[t])
        elif self.g2:
            col = colorsys.hsv_to_rgb(self.g[t], self.g2[t], 1)
        else:
            col = colorsys.hsv_to_rgb(self.g[t], 1, 1)
        return self.call_next(t, Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255)))

class Rainbow(ColorSource):

    def __init__(self, gen):
        super(Rainbow, self).__init__(gen)

    def describe(self):
        desc = common.make_function(common.FUNC_RAINBOW, (common.ARG_FUNC,))
        #print "%s(" % (self.__class__.__name__),
        if self.g:
            desc += self.g.describe()
        #print ")"
        return desc + self.describe_next()

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

        return self.call_next(t, Color(color[0], color[1], color[2]))

class CompColorSource(common.ChainLink):

    def __init__(self, hue, dist, index = 0):
        '''color - base color for the triad. const or gen
           index - which of the parts of the complement are we: 0 anchor, 1 secondary color 1, 2 secondary color 2
           dist - the distribution angle between secondary colors'''
        super(CompColorSource, self).__init__()
        self.color = color
        self.dist = dist
        self.index = index

        if type(self.index) in (int, float):
            self.index_f = None
        else:
            self.index_f = self.index
            self.index = self.index_f[0]

    def describe(self):
        args = [common.ARG_COLOR, common.ARG_FUNC]
        desc = common.pack_color(self.color)
        desc += self.dist.describe()

        if self.index_f:
            desc += self.index_f.describe()
            args.append(common.ARG_FUNC)
        else:
            desc += common.pack_fixed(self.index)
            args.append(common.ARG_VALUE)

        return common.make_function(common.FUNC_COMPLEMENTARY, args) + desc + self.describe_next()

    def __getitem__(self, t):
        if self.index == 0:
            return self.call_next(t, self.color)
        elif self.index == 1:
            h,s,v = colorsys.rgb_to_hsv(self.color.color[0] / 255.0, self.color.color[1] / 255.0, self.color.color[2] / 255.0)
            h = (h - self.dist) % 1.0
            col = colorsys.hsv_to_rgb(h, s, v)
            return self.call_next(t, Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255)))
        else:
            h,s,v = colorsys.rgb_to_hsv(self.color.color[0] / 255.0, self.color.color[1] / 255.0, self.color.color[2] / 255.0)
            h = (h + self.dist) % 1.0
            col = colorsys.hsv_to_rgb(h, s, v)
            return self.call_next(t, Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255)))

class SourceOp(common.ChainLink):
    def __init__(self, operation, src1, src2, src3 = None):
        super(SourceOp, self).__init__()
        if not isinstance(src1, ColorSource) or not isinstance(src2, ColorSource) or (src3 and not isinstance(src3, ColorSource)):
            raise TypeError("SourceOp needs to be passed two ColorSource objects")
        self.operation = operation
        self.s1 = src1
        self.s2 = src2
        self.s3 = src3

    def describe(self):
        if self.s3:
            desc = common.make_function(common.FUNC_SRCOP, (common.ARG_VALUE, common.ARG_FUNC,common.ARG_FUNC, common.ARG_FUNC))
        else:
            desc = common.make_function(common.FUNC_SRCOP, (common.ARG_VALUE, common.ARG_FUNC,common.ARG_FUNC))
        desc += common.pack_fixed(self.operation)
        desc += self.s1.describe()
        desc += self.s2.describe()
        if self.s3:
            desc += self.s3.describe()
        return desc + self.describe_next()

    def __getitem__(self, t):
        col1 = self.s1[t]
        col2 = self.s2[t]
        if self.s3:
            col3 = self.s3[t]
        else:
            col3 = Color(0,0,0)
        res = Color(0,0,0)
        if self.operation == common.OP_ADD:
            res.color[0] = max(0, min(255, col1.color[0] + col2.color[0] + col3.color[0]))
            res.color[1] = max(0, min(255, col1.color[1] + col2.color[1] + col3.color[1]))
            res.color[2] = max(0, min(255, col1.color[2] + col2.color[2] + col3.color[2]))
        elif self.operation == common.OP_SUB:
            res.color[0] = max(0, min(255, col1.color[0] - col2.color[0] - col3.color[0]))
            res.color[1] = max(0, min(255, col1.color[1] - col2.color[1] - col3.color[1]))
            res.color[2] = max(0, min(255, col1.color[2] - col2.color[2] - col3.color[2]))

        # Not sure if any of these make sense. :)
        elif self.operation == common.OP_MUL:
            res.color[0] = max(0, min(255, col1.color[0] * col2.color[0]))
            res.color[1] = max(0, min(255, col1.color[1] * col2.color[1]))
            res.color[2] = max(0, min(255, col1.color[2] * col2.color[2]))
        elif self.operation == common.OP_SUB:
            res.color[0] = max(0, min(255, col1.color[0] / col2.color[0]))
            res.color[1] = max(0, min(255, col1.color[1] / col2.color[1]))
            res.color[2] = max(0, min(255, col1.color[2] / col2.color[2]))
        elif self.operation == common.OP_MOD:
            res.color[0] = max(0, min(255, col1.color[0] % col2.color[0]))
            res.color[1] = max(0, min(255, col1.color[1] % col2.color[1]))
            res.color[2] = max(0, min(255, col1.color[2] % col2.color[2]))

        return self.call_next(t, res)

class RGBSource(common.ChainLink):
    def __init__(self, red, green = None, blue = None):
        super(RGBSource, self).__init__()
        if not isinstance(red, generator.GeneratorBase):
            raise TypeError("RGBSource needs to be passed Generator objects")
        if blue and not isinstance(blue, generator.GeneratorBase):
            raise TypeError("RGBSource needs to be passed Generator objects")
        if green and not isinstance(green, generator.GeneratorBase):
            raise TypeError("RGBSource needs to be passed Generator objects")
        self.red = red
        self.green = green
        self.blue = blue

    def describe(self):
        args = [common.ARG_FUNC]
        desc = self.red.describe()
        if self.green:
            args.append(common.ARG_FUNC)
            desc += self.green.describe()
        if self.blue:
            args.append(common.ARG_FUNC)
            desc += self.blue.describe()
        return common.make_function(common.FUNC_RGB_SRC, args) + desc + self.describe_next()

    def __getitem__(self, t):
        red = self.red[t]
        if self.blue:
            blue = self.blue[t]
        else:
            blue = 0
        if self.green:
            green = self.green[t]
        else:
            green = 0
        return self.call_next(t, Color(int(red * 255), int(green * 255), int(blue * 255)))
