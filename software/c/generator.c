#include <stdio.h>
#include <math.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>

#include "sin_table.h"

#define SCALE_FACTOR 1000
#define S_PIM2       6283 // PI * 2 * SCALE_FACTOR
#define S_PI         3141 // PI * SCALE_FACTOR
#define S_PID2       1570 // PI / 2 * SCALE_FACTOR

class Generator
{
    public:
        Generator(int32_t _period, int32_t _phase, int32_t _amplitude, int32_t _offset)
        {
            period = _period;
            phase = _phase;
            amplitude = _amplitude;
            offset = _offset;
        };

        int32_t calculate(uint32_t t) = 0;

    protected:

        int32_t period, phase, amplitude, offset;
};

class SinGenerator : Generator
{
    public:

        int32_t calculate(uint32_t t)
        {
            int32_t index = (((int32_t)t * period / SCALE_FACTOR + phase) % S_PIM2) * NUM_SIN_TABLE_ENTRIES / S_PIM2;
            if (index < 0)
                index = NUM_SIN_TABLE_ENTRIES + index;
            return (int32_t)sin_table[index] * amplitude / SCALE_FACTOR + offset;
        }
}

int32_t generator_square(uint32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    int32_t v = ((int32_t)t * SCALE_FACTOR / period) + phase;
    if (v % SCALE_FACTOR >= (SCALE_FACTOR >> 1))
        return amplitude + offset;
    else
        return offset;
}

int32_t generator_sawtooth(uint32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    int32_t v = (((int32_t)t * period / SCALE_FACTOR) + phase) % SCALE_FACTOR;
    return v * amplitude / SCALE_FACTOR + offset;
}

int32_t generator_step(uint32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    int32_t v = ((int32_t)t * SCALE_FACTOR / period) + phase;
    if (v >= 0)
        return amplitude + offset;
    else
        return offset;
}

