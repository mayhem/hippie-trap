#include <stdlib.h>
#include <avr/pgmspace.h>
#include "function.h"
#include "colorspace.h"

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

void f_rainbow_init(void *_self, int32_t period)
{
    rainbow_t *self = (rainbow_t *)_self;
    
    self->period = (int32_t)SCALE_FACTOR * (int32_t)SCALE_FACTOR/ period;    
}

int32_t f_error(void *self, int32_t t)
{
    t /= 500;

    return t % 2 ? 64 : 0;
}

int32_t f_sin(void *_self, int32_t t)
{
    return 0;
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

int32_t f_rainbow(void *_self, int32_t t, uint8_t led)
{
    rainbow_t *self = (rainbow_t *)_self;
    color_t color;
    uint8_t *ptr = (uint8_t *)&color;

    int32_t h = ((int32_t)t * SCALE_FACTOR / self->g.period);
    h += 250 * (led / 3);

    hsv_to_rgb(h, SCALE_FACTOR, SCALE_FACTOR, &color);

    return (ptr[led % 3]) * SCALE_FACTOR / 255;
}
