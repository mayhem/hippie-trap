#ifndef __GENERATOR_H__
#define __GENERATOR_H__

#include <stdio.h>
#include <math.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include "defs.h"

#include "sin_table.h"

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

        virtual int32_t calculate(uint32_t t) = 0;

    protected:

        int32_t period, phase, amplitude, offset;
};

class SinGenerator : Generator
{
    public:

        SinGenerator(int32_t period, int32_t phase, int32_t amplitude, int32_t offset) :
            Generator(period, phase, amplitude, offset) 
        {
        };
        int32_t calculate(uint32_t t)
        {
            int32_t index = (((int32_t)t * period / SCALE_FACTOR + phase) % S_PIM2) * NUM_SIN_TABLE_ENTRIES / S_PIM2;
            if (index < 0)
                index = NUM_SIN_TABLE_ENTRIES + index;
            return (int32_t)sin_table[index] * amplitude / SCALE_FACTOR + offset;
        };
};

class SquareGenerator : Generator
{
    public:

        SquareGenerator(int32_t period, int32_t phase, int32_t amplitude, int32_t offset) :
            Generator(period, phase, amplitude, offset) 
        {
        };
        int32_t calculate(uint32_t t)
        {
            int32_t v = ((int32_t)t * SCALE_FACTOR / period) + phase;
            if (v % SCALE_FACTOR >= (SCALE_FACTOR >> 1))
                return amplitude + offset;
            else
                return offset;
        }
};

class SawtoothGenerator : Generator
{
    public:

        SawtoothGenerator(int32_t period, int32_t phase, int32_t amplitude, int32_t offset) :
            Generator(period, phase, amplitude, offset) 
        {
        };
        int32_t calculate(uint32_t t)
        {
            int32_t v = (((int32_t)t * period / SCALE_FACTOR) + phase) % SCALE_FACTOR;
            return v * amplitude / SCALE_FACTOR + offset;
        }
};

class StepGenerator : Generator
{
    public:

        StepGenerator(int32_t period, int32_t phase, int32_t amplitude, int32_t offset) :
            Generator(period, phase, amplitude, offset) 
        {
        };
        int32_t calculate(uint32_t t)
        {
            int32_t v = ((int32_t)t * SCALE_FACTOR / period) + phase;
            if (v >= 0)
                return amplitude + offset;
            else
                return offset;
        }
};
#endif
