#include <stdlib.h>
#include <Arduino.h>
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

void g_square_init(void *_self, g_method method, int32_t period, int32_t phase, int32_t amplitude, int32_t offset, int32_t duty)
{
    square_t *self = (square_t *)_self;
    self->method = method;
    self->period = period;
    self->phase = phase;
    self->amplitude = amplitude;
    self->offset = offset;
    self->duty = duty;
}

int32_t g_sin(void *_self, uint32_t t)
{
    int16_t value;
    
    generator_t *self = (generator_t *)_self;
    int32_t index = (((int32_t)t * self->period / SCALE_FACTOR + self->phase) % S_PIM2) * NUM_SIN_TABLE_ENTRIES / S_PIM2;
    if (index < 0)
        index = NUM_SIN_TABLE_ENTRIES + index;
 
    // first explicitly cast to int16_t, to make sure negative numbers are handled correctly
    value = (int16_t)pgm_read_word_near(sin_table + index);
    return (int32_t)value * self->amplitude / SCALE_FACTOR + self->offset;
}

int32_t g_square(void *_self, uint32_t t)
{
    square_t *self = (square_t *)_self;
    int32_t v = ((int32_t)t * SCALE_FACTOR / self->period) + self->phase;
    if (v % SCALE_FACTOR >= self->duty)
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

void g_generator_op_init(void *_self, uint8_t op, generator_t *g, generator_t *g2)
{
    generator_op_t *self = (generator_op_t *)_self;
    self->g = g;
    self->g2 = g2;
    self->op = op;
}

int32_t g_generator_op_get(void *_self, uint32_t t)
{
    generator_op_t *self = (generator_op_t *)_self;
    int32_t         v1, v2;

    v1 = self->g->method(self->g, t);
    v2 = self->g2->method(self->g2, t);

    switch(self->op)
    {
        case OP_ADD:
            return v1 + v2;
        case OP_SUB:
            return v1 - v2;
        case OP_MUL:
            return v1 * v2;
        case OP_DIV:
            return v1 * SCALE_FACTOR / v2;
        case OP_MOD:
            return v1 % v2;
    }
    return 0;
}
