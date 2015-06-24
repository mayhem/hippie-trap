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
        desc = common.make_function(common.FUNC_RAND_COL_SEQ, (common.ARG_VALUE,common.ARG_VALUE))

        args = []
        desc = bytearray()

        if type(self.period) in (int, float):
            desc += common.pack_fixed(self.period)
            args.append(common.ARG_VALUE)
        else:
            desc += self.period_f.describe()
            args.append(common.ARG_FUNC)

        if type(self.seed) in (int, float):
            desc += common.pack_fixed(self.seed)
            args.append(common.ARG_VALUE)
        else:
            desc += self.seed_f.describe()
            args.append(common.ARG_FUNC)

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

    def __init__(self, color, dist, index):
        '''color - base color for the triad. const or gen
           index - which of the parts of the complement are we: 0 anchor, 1 secondary color 1, 2 secondary color 2
           dist - the distribution angle between secondary colors'''
        super(CompColorSource, self).__init__()
        self.color = color
        self.dist = dist
        self.index = index

        if type(self.dist) in (int, float):
            self.dist_f = None
        else:
            self.dist_f = self.dist
            self.dist = self.dist_f[0]

        if type(self.index) in (int, float):
            self.index_f = None
        else:
            self.index_f = self.index
            self.index = self.index_f[0]

    def describe(self):
        args = []
        desc = self.color.describe()

        if type(self.dist) in (int, float):
            desc += common.pack_fixed(self.dist)
            args.append(common.ARG_VALUE)
        else:
            desc += self.dist_f.describe()
            args.append(common.ARG_FUNC)

        if type(self.index) in (int, float):
            desc += common.pack_fixed(self.index)
            args.append(common.ARG_VALUE)
        else:
            desc += self.index_f.describe()
            args.append(common.ARG_FUNC)

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
            desc += self.s2.describe()
        return desc + self.describe_next()

    def __getitem__(self, t):
        col1 = self.s1[t]
        col2 = self.s2[t]
        if self.s3:
            col3 = self.s3[t]
        else:
            colr3 = Color(0,0,0)
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
