#include <stdlib.h>
#include "generator.h"

void g_generator_init(generator_t *self, g_method method, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    self->method = method;
    self->period = period;
    self->phase = phase;
    self->amplitude = amplitude;
    self->offset = offset;
}

int32_t g_sin(generator_t *self, uint32_t t)
{
    int32_t index = (((int32_t)t * self->period / SCALE_FACTOR + self->phase) % S_PIM2) * NUM_SIN_TABLE_ENTRIES / S_PIM2;
    if (index < 0)
        index = NUM_SIN_TABLE_ENTRIES + index;
    return (int32_t)sin_table[index] * self->amplitude / SCALE_FACTOR + self->offset;
}

int32_t g_square(generator_t *self, uint32_t t)
{
    int32_t v = ((int32_t)t * SCALE_FACTOR / self->period) + self->phase;
    if (v % SCALE_FACTOR >= (SCALE_FACTOR >> 1))
        return self->amplitude + self->offset;
    else
        return self->offset;
}

int32_t g_sawtooth(generator_t *self, uint32_t t)
{
    int32_t v = (((int32_t)t * self->period / SCALE_FACTOR) + self->phase) % SCALE_FACTOR;
    return v * self->amplitude / SCALE_FACTOR + self->offset;
}

int32_t g_step(generator_t *self, uint32_t t)
{
    int32_t v = ((int32_t)t * SCALE_FACTOR / self->period) + self->phase;
    if (v >= 0)
        return self->amplitude + self->offset;
    else
        return self->offset;
}
