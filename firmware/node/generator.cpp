#include <stdlib.h>
#include <avr/pgmspace.h>
#include "generator.h"

void g_generator_init(void *_self, g_method method, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    generator_t *self = (generator_t *)_self;
    self->method = method;
    self->period = period;
    self->phase = phase;
    self->amplitude = amplitude;
    self->offset = offset;
}

int32_t g_sin(void *_self, uint32_t t)
{
    generator_t *self = (generator_t *)_self;
    int32_t index = (((int32_t)t * self->period / SCALE_FACTOR + self->phase) % S_PIM2) * NUM_SIN_TABLE_ENTRIES / S_PIM2;
    if (index < 0)
        index = NUM_SIN_TABLE_ENTRIES + index;

    return (int32_t)pgm_read_word_near(sin_table + index) * self->amplitude / SCALE_FACTOR + self->offset;
}

int32_t g_square(void *_self, uint32_t t)
{
    generator_t *self = (generator_t *)_self;
    int32_t v = ((int32_t)t * SCALE_FACTOR / self->period) + self->phase;
    if (v % SCALE_FACTOR >= (SCALE_FACTOR >> 1))
        return self->amplitude + self->offset;
    else
        return self->offset;
}

int32_t g_sawtooth(void *_self, uint32_t t)
{
    generator_t *self = (generator_t *)_self;
    int32_t v = (((int32_t)t * self->period / SCALE_FACTOR) + self->phase) % SCALE_FACTOR;
    return v * self->amplitude / SCALE_FACTOR + self->offset;
}

int32_t g_step(void *_self, uint32_t t)
{
    generator_t *self = (generator_t *)_self;
    int32_t v = ((int32_t)t * SCALE_FACTOR / self->period) + self->phase;
    if (v >= 0)
        return self->amplitude + self->offset;
    else
        return self->offset;
}
