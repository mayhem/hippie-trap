#include <stdlib.h>
#include <avr/pgmspace.h>
#include "function.h"

int32_t pmod(int32_t val, int32_t mod)
{
    int32_t temp = val % mod;        
    return (temp < 0) ? mod + temp : temp;
}

void f_generator_init(void *_self, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    generator_t *self = (generator_t *)_self;
    self->period = period;
    self->phase = phase;
    self->amplitude = amplitude;
    self->offset = offset;
}

void f_sin_init(void *_self, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    generator_t *self = (generator_t *)_self;
    
    self->period = (int32_t)S_PIM2 * (int32_t)SCALE_FACTOR / period;    
    self->phase = -S_PID2 + (S_PIM2 * phase / SCALE_FACTOR);
    self->amplitude = amplitude;
    self->offset = offset;
}

void f_square_init(void *_self, int32_t period, int32_t phase, int32_t amplitude, int32_t offset, int32_t duty)
{
    square_t *self = (square_t *)_self;
    self->g.period = period;
    self->g.phase = phase;    
    self->g.amplitude = amplitude;
    self->g.offset = offset;
    self->duty = duty;
}

void f_sawtooth_init(void *_self, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    generator_t *self = (generator_t *)_self;
    
    self->period = (int32_t)SCALE_FACTOR * (int32_t)SCALE_FACTOR/ period;    
    self->phase = phase;
    self->amplitude = amplitude;
    self->offset = offset;
}

int32_t f_sin(void *_self, int32_t t)
{
    int16_t value;
    
    generator_t *self = (generator_t *)_self;
    int32_t index = (((int32_t)t * self->period / SCALE_FACTOR + self->phase) % S_PIM2) * NUM_SIN_TABLE_ENTRIES / S_PIM2;
    if (index < 0)
        index += NUM_SIN_TABLE_ENTRIES;

    // first explicitly cast to int16_t, to make sure negative numbers are handled correctly
    value = (int16_t)pgm_read_word_near(sin_table + index);
    return (int32_t)value * self->amplitude / SCALE_FACTOR + self->offset;
}

int32_t f_square(void *_self, int32_t t)
{
    square_t *self = (square_t *)_self;

    int32_t v = ((int32_t)t * SCALE_FACTOR / self->g.period) + self->g.phase;
    if (pmod(v, SCALE_FACTOR) < self->duty)
        return self->g.amplitude + self->g.offset;
    else
        return self->g.offset;
}

int32_t f_sawtooth(void *_self, int32_t t)
{
    generator_t *self = (generator_t *)_self;  
    

    int32_t v = (((int32_t)t * self->period / SCALE_FACTOR) + self->phase) % SCALE_FACTOR;
    return v * self->amplitude / SCALE_FACTOR + self->offset;
}

int32_t f_step(void *_self, int32_t t)
{
    generator_t *self = (generator_t *)_self;


    int32_t v = ((int32_t)t * SCALE_FACTOR / self->period) + self->phase;
    if (v >= 0)
        return self->amplitude + self->offset;
    else
        return self->offset;
}

int32_t f_impulse(void *_self, int32_t t)
{
    generator_t *self = (generator_t *)_self;


    int32_t v = ((int32_t)t * SCALE_FACTOR / self->period) + self->phase;
    if (v >= 0 && v < SCALE_FACTOR)
        return self->amplitude + self->offset;
    else
        return self->offset;
}

int32_t f_line(void *_self, int32_t t)
{
    generator_t *self = (generator_t *)_self;
    return ((int32_t)t * self->amplitude / SCALE_FACTOR) + self->offset;
}

int32_t f_error(void *_self, int32_t t)
{
    t /= 500;

    return (t % 2 == 0) ? 64 : 0;
}
