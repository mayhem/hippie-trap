#include <Arduino.h>
#include <stdlib.h>
#include "generator.h"
#include "source.h"

void hsv_to_rgb(int32_t h, int32_t s, int32_t v, color_t *color)
{
    uint16_t hue;
    uint8_t  r, g, b, sat, val;
    uint8_t  base;

    if (s == 0) 
    {
        color->c[0]=val;
        color->c[1]=val;
        color->c[2]=val;  
        return;
    } 

    hue = h * 360 / SCALE_FACTOR; 
    sat = s * 255 / SCALE_FACTOR; 
    val = v * 255 / SCALE_FACTOR; 

    base = ((255 - sat) * val)>>8;

    switch(hue/60) 
    {
        case 0:
            r = val;
            g = (((val-base)*hue)/60)+base;
            b = base;
            break;

        case 1:
            r = (((val-base)*(60-(hue%60)))/60)+base;
            g = val;
            b = base;
            break;

        case 2:
            r = base;
            g = val;
            b = (((val-base)*(hue%60))/60)+base;
            break;

        case 3:
            r = base;
            g = (((val-base)*(60-(hue%60)))/60)+base;
            b = val;
            break;

        case 4:
            r = (((val-base)*(hue%60))/60)+base;
            g = base;
            b = val;
            break;

        case 5:
            r = val;
            g = base;
            b = (((val-base)*(60-(hue%60)))/60)+base;
            break;
    }
    color->c[0] = r;
    color->c[1] = g;
    color->c[2] = b;
}

void s_constant_color_init(s_constant_color_t *self, color_t *color)
{
    self->color.c[0] = color->c[0];
    self->color.c[1] = color->c[1];
    self->color.c[2] = color->c[2];
    self->method = s_constant_color_get;
    self->next = NULL; 
}

void s_constant_color_get(void *self, uint32_t t, color_t *dest)
{
    dest->c[0] = ((s_constant_color_t *)self)->color.c[0];
    dest->c[1] = ((s_constant_color_t *)self)->color.c[1];
    dest->c[2] = ((s_constant_color_t *)self)->color.c[2];
}

//--

void s_random_color_seq_init(s_random_color_seq_t *self, int32_t period, uint32_t seed)
{
    self->period = period;
    self->seed = seed;
    self->method = s_random_color_seq_get;
    self->next = NULL; 

    // Make sure we have a good random number saved before we set a predicatable seed
    g_random_seed = random();
}

void s_random_color_seq_get(void *self, uint32_t t, color_t *dest)
{
    randomSeed(((s_random_color_seq_t *)self)->seed + (uint32_t)(t * SCALE_FACTOR / ((s_random_color_seq_t *)self)->period));
    hsv_to_rgb(random(SCALE_FACTOR), SCALE_FACTOR, SCALE_FACTOR, dest);
}

//--

void s_hsv_init(s_hsv_t *self, generator_t *gen1, generator_t *gen2, generator_t *gen3)
{
    self->gen1 = gen1;
    self->gen2 = gen2;
    self->gen3 = gen3;
    self->method = s_hsv_get;
    self->next = NULL; 
}

void s_hsv_get(void *_self, uint32_t t, color_t *dest)
{
    s_hsv_t *self = (s_hsv_t *)_self;

    if (self->gen2 && self->gen3)
        hsv_to_rgb(self->gen1->method(self->gen1, t), self->gen2->method(self->gen2, t), self->gen3->method(self->gen2, t), dest);
    else
    if (self->gen2)
        hsv_to_rgb(self->gen1->method(self->gen1, t), self->gen2->method(self->gen2, t), SCALE_FACTOR, dest);
    else
        hsv_to_rgb(self->gen1->method(self->gen1, t), SCALE_FACTOR, SCALE_FACTOR, dest);
}

//--

void s_rainbow_init(s_rainbow_t *self, generator_t *gen)
{
    self->gen = gen;
    self->method = s_rainbow_get;
    self->next = NULL; 
}

void s_rainbow_get(void *_self, uint32_t t, color_t *dest)
{
    uint8_t wheel_pos;

    s_rainbow_t *self = (s_rainbow_t *)_self;
    wheel_pos = 255 - (255 * self->gen->method(self->gen, t) / SCALE_FACTOR);
    if (wheel_pos < 85)
    {
        dest->c[0] = 255 - wheel_pos * 3;
        dest->c[1] = 0;
        dest->c[2] = wheel_pos * 3;
    }
    else
    if (wheel_pos < 170)
    {
        wheel_pos -= 85;
        dest->c[0] = 0;
        dest->c[1] = wheel_pos * 3;
        dest->c[2] = 255 - wheel_pos * 3;
    }
    else
    {
        wheel_pos -= 170;
        dest->c[0] = wheel_pos * 3;
        dest->c[1] = 255 - (wheel_pos * 3);
        dest->c[2] = 0;
    }
}
