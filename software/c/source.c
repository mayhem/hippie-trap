#include <stdlib.h>
//#include "generator.h"
#include "source.h"

void hsv_to_rgb(int32_t hue, int32_t sat, int32_t value, color_t *color)
{
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
}

void s_random_color_seq_get(void *self, uint32_t t, color_t *dest)
{
    srand(((s_random_color_seq_t *)self)->seed + (uint32_t)(t * SCALE_FACTOR / ((s_random_color_seq_t *)self)->period));
    hsv_to_rgb(rand() % SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR, dest);
}

//--

void s_hsv_init(s_hsv_t *self, g_method gen1, g_method gen2, g_method gen3)
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
        hsv_to_rgb(self->gen1(_self, t), self->gen2(_self, t), self->gen3(_self, t), dest);
    else
    if (self->gen2)
        hsv_to_rgb(self->gen1(_self, t), self->gen2(_self, t), 1.0, dest);
    else
        hsv_to_rgb(self->gen1(_self, t), 1.0, 1.0, dest);
}

//--

void s_rainbow_init(s_rainbow_t *self, g_method gen)
{
    self->gen = gen;
    self->method = s_rainbow_get;
    self->next = NULL; 
}

void s_rainbow_get(void *self, uint32_t t, color_t *dest)
{
    uint8_t wheel_pos;

    wheel_pos = 255 - (255 * ((s_hsv_t *)self)->gen1(self, t) / SCALE_FACTOR);
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
