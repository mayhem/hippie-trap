#include <stdlib.h>
#include "defs.h"

color_t hsv_to_rgb(int32_t hue, int32_t sat, int32_t value)
{



}

color_t function_constant_color(color_t col)
{
    return col;
}

color_t function_random_color_sequence(uint32_t t, int32_t period, uint32_t seed)
{
    srand((uint32_t)(t * SCALE_FACTOR / period));
    return hsv_to_rgb(rand() % SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR);
}

color_t function_hsv(uint32_t t, 
                     int32_t (*gen)(uint32_t, int32_t, int32_t, int32_t, int32_t),
                     int32_t (*gen2)(uint32_t, int32_t, int32_t, int32_t, int32_t),
                     int32_t (*gen3)(uint32_t, int32_t, int32_t, int32_t, int32_t))
{
    if (gen2 && gen3)
        col = colorsys.hsv_to_rgb(self.g[t], self.gen2[t], self.gen3[t])
    else
    if (gen2)
        col = colorsys.hsv_to_rgb(self.g[t], self.gen2[t], 1)
    else
        col = colorsys.hsv_to_rgb(self.g[t], 1, 1)
            return self.call_next(t, Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255)))
}

class ColorWheel(ColorSource):

    def __init__(self, period = 1.0, phase = 0.0, gen = None):
        if gen:
            g = gen
        else:
            g = generator.Sawtooth(period, phase)
        super(Rainbow, self).__init__(g)

    def describe(self):
        desc = common.make_function(common.FUNC_COLOR_WHEEL, (common.ARG_VALUE,common.ARG_VALUE,common.ARG_FUNC))
        desc += common.pack_fixed(self.period)
        desc += common.pack_fixed(self.seed)
        print "%s(" % (self.__class__.__name__),
        if self.g:
            desc += self.g.describe()
        print ")"
        return desc + self.describe_next()

    def __getitem__(self, t):
        col = colorsys.hsv_to_rgb(self.g[t], 1, 1)
        return self.call_next(t, Color(int(col[0] * 255), int(col[1] * 255), int(col[2] * 255)))

class Rainbow(ColorSource):

    def __init__(self, gen):
        super(Rainbow, self).__init__(gen)

    def describe(self):
        desc = common.make_function(common.FUNC_RAINBOW, (common.ARG_FUNC,))
        print "%s(" % (self.__class__.__name__),
        if self.g:
            desc += self.g.describe()
        print ")"
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
