#include <stdlib.h>
#include "filter.h"
#include "generator.h"

void f_fade_in_init(f_fade_in_t *self, f_method method, int32_t duration, int32_t offset)
{
    self->duration = duration;
    self->method = method;
    self->offset = offset;
    self->method = f_fade_in_get;
}

void f_fade_in_get(void *_self, uint32_t t, color_t *src, color_t *dest)
{
    f_fade_in_t *self = (f_fade_in_t *)self;
    if (t < self->offset)
    {
        dest->c[0] = dest->c[1] = dest->c[2] = 0;
        return;
    }
    if (t < self->offset + self->duration)
    {
        int32_t percent = (t - self->offset) * SCALE_FACTOR / self->duration;
        dest->c[0] = src->c[0] * percent / SCALE_FACTOR;
        dest->c[1] = src->c[1] * percent / SCALE_FACTOR;
        dest->c[2] = src->c[2] * percent / SCALE_FACTOR;
    }
}

void f_fade_out_init(f_fade_out_t *self, f_method method,  int32_t duration, int32_t offset)
{
    self->duration = duration;
    self->method = method;
    self->offset = offset;
    self->method = f_fade_out_get;
}

void f_fade_out_get(void *_self, uint32_t t, color_t *src, color_t *dest)
{
    f_fade_out_t *self = (f_fade_out_t *)self;
    if (t >= self->offset + self->duration)
    {
        dest->c[0] = dest->c[1] = dest->c[2] = 0;
        return;
    }
    if (t > self->offset)
    {
        int32_t percent = SCALE_FACTOR - ((t - self->offset) * SCALE_FACTOR / self->duration);
        dest->c[0] = src->c[0] * percent / SCALE_FACTOR;
        dest->c[1] = src->c[1] * percent / SCALE_FACTOR;
        dest->c[2] = src->c[2] * percent / SCALE_FACTOR;
    }
}

void f_brightness_init(f_brightness_t *self, f_method method, generator_t *gen)
{
    printf("brightness init: %p\n", self);
    self->gen = gen;
    self->method = method;
    self->method = f_brightness_get;
}

void f_brightness_get(void *_self, uint32_t t, color_t *src, color_t *dest)
{
    f_brightness_t *self = (f_brightness_t *)_self;

    printf("in brightness filter: %p %p\n", self, _self);
    printf("src color: %d, %d, %d\n", src->c[0], src->c[1], src->c[2]);

    int32_t percent = self->gen->method(_self, t);
    printf("percent: %d\n", percent);
    dest->c[0] = src->c[0] * percent / SCALE_FACTOR;
    dest->c[1] = src->c[1] * percent / SCALE_FACTOR;
    dest->c[2] = src->c[2] * percent / SCALE_FACTOR;
}
