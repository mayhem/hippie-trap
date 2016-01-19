#include <stdlib.h>
#include <Arduino.h>
#include "filter.h"
#include "generator.h"
#include "source.h"

void f_fade_in_init(f_fade_in_t *self, f_method method, int32_t duration, int32_t offset)
{
    self->duration = duration;
    self->method = method;
    self->offset = offset;
    self->method = f_fade_in_get;
    self->next = NULL;
}

uint8_t f_fade_in_get(void *_self, uint32_t t, color_t *src, color_t *dest)
{
    f_fade_in_t *self = (f_fade_in_t *)_self;
    
    if (t < self->offset)
    {
        dest->c[0] = dest->c[1] = dest->c[2] = 0;
        return 1;
    }
    if (t < self->offset + self->duration)
    {
        int32_t percent = (t - self->offset) * SCALE_FACTOR / self->duration;
        
        dest->c[0] = src->c[0] * percent / SCALE_FACTOR;
        dest->c[1] = src->c[1] * percent / SCALE_FACTOR;
        dest->c[2] = src->c[2] * percent / SCALE_FACTOR;
        return 1;
    }
    dest->c[0] = src->c[0];
    dest->c[1] = src->c[1];
    dest->c[2] = src->c[2];

    return 1;
}

void f_fade_out_init(f_fade_out_t *self, f_method method,  int32_t duration, int32_t offset)
{
    self->duration = duration;
    self->method = method;
    self->offset = offset;
    self->method = f_fade_out_get;
    self->next = NULL;
}

uint8_t f_fade_out_get(void *_self, uint32_t t, color_t *src, color_t *dest)
{
    f_fade_out_t *self = (f_fade_out_t *)_self;
    if (t >= self->offset + self->duration)
    {
        dest->c[0] = dest->c[1] = dest->c[2] = 0;
        return 1;
    }
    if (t >= self->offset)
    {
        int32_t percent = SCALE_FACTOR - ((t - self->offset) * SCALE_FACTOR / self->duration);
        dest->c[0] = src->c[0] * percent / SCALE_FACTOR;
        dest->c[1] = src->c[1] * percent / SCALE_FACTOR;
        dest->c[2] = src->c[2] * percent / SCALE_FACTOR;
        return 1;
    }
    dest->c[0] = src->c[0];
    dest->c[1] = src->c[1];
    dest->c[2] = src->c[2];

    return 1;
}

void f_brightness_init(f_brightness_t *self, generator_t *gen)
{
    self->gen = gen;
    self->method = f_brightness_get;
    self->next = NULL;
}

uint8_t f_brightness_get(void *_self, uint32_t t, color_t *src, color_t *dest)
{
    f_brightness_t *self = (f_brightness_t *)_self;

    int32_t percent = self->gen->method(self->gen, t);
    dest->c[0] = src->c[0] * percent / SCALE_FACTOR;
    dest->c[1] = src->c[1] * percent / SCALE_FACTOR;
    dest->c[2] = src->c[2] * percent / SCALE_FACTOR;

    return 1;
}

void f_color_shift_init(f_color_shift_t *self, int32_t h_shift, int32_t s_shift, int32_t v_shift)
{
    self->method = f_color_shift_get;
    self->next = NULL;
    self->h_shift = h_shift;
    self->s_shift = s_shift;
    self->v_shift = v_shift;
}

// r: 0 g: 252 b: 0 - h 333 s 1000 v 988  -  r: 0 g: 254 b: 148
// r: 0 g: 0 b: 0 - h 0 s 0 v 0  -  r: 252 g: 151 b: 0
// r: 0 g: 2 b: 0 - h 333 s 1000 v 7  -  r: 0 g: 254 b: 148

uint8_t f_color_shift_get(void *_self, uint32_t t, color_t *src, color_t *dest)
{
    int32_t h, s, v;
    
    f_color_shift_t *self = (f_color_shift_t *)_self;

    if (self->h_shift == 0 && self->s_shift == 0 && self->v_shift == 0)
    {
        dest->c[0] = src->c[0];
        dest->c[1] = src->c[1];
        dest->c[2] = src->c[2];
        return 1; 
    }           

    if (!rgb_to_hsv(src, &h, &s, &v))

        return 0;

    h = (h + self->h_shift) % SCALE_FACTOR;
    v = max(min(v + self->v_shift, SCALE_FACTOR - 1), 0);
    s = max(min(v + self->s_shift, SCALE_FACTOR - 1), 0);    
    
    return hsv_to_rgb(h, s, v, dest);
}
