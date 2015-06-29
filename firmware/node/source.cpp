#include <Arduino.h>
#include <stdlib.h>
#include "generator.h"
#include "source.h"
#include "parse.h"

void print_col(color_t *c)
{
    Serial.print(c->c[0], DEC);
    Serial.print(", ");
    Serial.print(c->c[1], DEC);
    Serial.print(", ");
    Serial.print(c->c[2], DEC);
}


uint8_t hsv_to_rgb(int32_t h, int32_t s, int32_t v, color_t *color)
{
    uint16_t hue;
    uint8_t  r, g, b, sat, val;
    uint8_t  base;
    
    if (h >= SCALE_FACTOR)
        h = SCALE_FACTOR - 1;
    if (s >= SCALE_FACTOR)
        s = SCALE_FACTOR - 1;
    if (v >= SCALE_FACTOR)
        v = SCALE_FACTOR - 1;
    if (h < 0)
        h = 0;
    if (s < 0)
        s = 0;
    if (v < 0)
        v = 0;
          
    hue = h * 360 / SCALE_FACTOR; 
    sat = s * 255 / SCALE_FACTOR; 
    val = v * 255 / SCALE_FACTOR; 

    if (sat == 0) 
    {
        color->c[0]=val;
        color->c[1]=val;
        color->c[2]=val;   
        return 0;
    } 

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

    return 1;
}

uint8_t rgb_to_hsv(color_t *col, int32_t *_h, int32_t *_s, int32_t *_v)
{
    int32_t rd = ((int32_t)col->c[0] * (int32_t)SCALE_FACTOR)/(int32_t)255;
    int32_t gd = ((int32_t)col->c[1] * (int32_t)SCALE_FACTOR)/(int32_t)255;
    int32_t bd = ((int32_t)col->c[2] * (int32_t)SCALE_FACTOR)/(int32_t)255;
    int32_t mx = max(rd, max(gd, bd)); 
    int32_t mn = min(rd, min(gd, bd));
    int32_t h, s, v = mx;

    int32_t d = mx - mn;
    s = mx == 0 ? 0 : d * SCALE_FACTOR / mx;

    if (mx == 0)
        return 0;
    
    //Serial.print("r " + String(col->c[0]));
    //Serial.print(" g " + String(col->c[1]));
    //Serial.println(" b " + String(col->c[2]));
    
    if (mx == mn) 
    { 
        h = 0; 
    } 
    else 
    {
        if (mx == rd) 
            h = (gd - bd) * SCALE_FACTOR / d + (gd < bd ? 6000 : 0);
        else 
        if (mx == gd) 
            h = (bd - rd) * SCALE_FACTOR / d + 2000;
        else 
        if (mx == bd) 
            h = (rd - gd) * SCALE_FACTOR / d + 4000;
        h = h / 6;
    }

    //Serial.print("h " + String(h));
    //Serial.print(" s " + String(s));
    //Serial.println(" v " + String(v));
    
    *_h = h;
    *_s = s;
    *_v = v;

    return 1;
}

//--

void s_constant_color_init(s_constant_color_t *self, color_t *color)
{
    self->color.c[0] = color->c[0];
    self->color.c[1] = color->c[1];
    self->color.c[2] = color->c[2];
    self->method = s_constant_color_get;
    self->next = NULL; 
}

uint8_t s_constant_color_get(void *self, uint32_t t, color_t *dest)
{
    dest->c[0] = ((s_constant_color_t *)self)->color.c[0];
    dest->c[1] = ((s_constant_color_t *)self)->color.c[1];
    dest->c[2] = ((s_constant_color_t *)self)->color.c[2];

    return 1;
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

uint8_t s_random_color_seq_get(void *self, uint32_t t, color_t *dest)
{
    uint32_t seed = ((s_random_color_seq_t *)self)->seed;
    
    if (seed)
        randomSeed(seed + (uint32_t)(t / ((s_random_color_seq_t *)self)->period));
    return hsv_to_rgb(random(SCALE_FACTOR), SCALE_FACTOR, SCALE_FACTOR, dest);
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

uint8_t s_hsv_get(void *_self, uint32_t t, color_t *dest)
{
    s_hsv_t *self = (s_hsv_t *)_self;

    if (self->gen2 && self->gen3)    
        return hsv_to_rgb(self->gen1->method(self->gen1, t), self->gen2->method(self->gen2, t), self->gen3->method(self->gen3, t), dest);     
    else
    if (self->gen2)
        return hsv_to_rgb(self->gen1->method(self->gen1, t), self->gen2->method(self->gen2, t), SCALE_FACTOR, dest);
    else
        return hsv_to_rgb(self->gen1->method(self->gen1, t), SCALE_FACTOR, SCALE_FACTOR, dest);
}

//--

void s_rgb_init(s_rgb_t *self, generator_t *red, generator_t *green, generator_t *blue)
{

    self->method = s_rgb_get;
    self->next = NULL; 
    self->red = red;
    self->green = green;
    self->blue = blue;
}

uint8_t s_rgb_get(void *_self, uint32_t t, color_t *dest)
{
    s_rgb_t *self = (s_rgb_t *)_self;
    int32_t red, green, blue;

    red = self->red->method(self->red, t);
    if (self->green)
        green = self->green->method(self->green, t);
    else
        green = 0;
        
    if (self->blue)
        blue = self->blue->method(self->blue, t);
    else
        blue = 0;

    dest->c[0] = red * 255 / SCALE_FACTOR;
    dest->c[1] = green * 255 / SCALE_FACTOR;
    dest->c[2] = blue *255 / SCALE_FACTOR;
    
    return 1;
}

//--

void s_rainbow_init(s_rainbow_t *self, generator_t *gen)
{
    self->gen = gen;
    self->method = s_rainbow_get;
    self->next = NULL; 
}

uint8_t s_rainbow_get(void *_self, uint32_t t, color_t *dest)
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
    return 1;
}

//--

void s_op_init(s_op_t *self, uint8_t op, s_source_t *s1, s_source_t *s2)
{
    self->method = s_op_get;
    self->next = NULL; 
    self->s1 = s1;
    self->s2 = s2;
}


uint8_t s_op_get(void *_self, uint32_t t, color_t *dest)
{
    s_op_t *self = (s_op_t *)_self;
    color_t col1, col2;

    sub_evaluate(self->s1, t, &col1);
    sub_evaluate(self->s2, t, &col2);

    switch(self->op)
    {
        case OP_ADD:
            dest->c[0] = max(0, min(255, col1.c[0] + col2.c[0]));
            dest->c[1] = max(0, min(255, col1.c[1] + col2.c[1]));
            dest->c[2] = max(0, min(255, col1.c[2] + col2.c[2]));
            break;
        case OP_SUB:
            dest->c[0] = max(0, min(255, col1.c[0] - col2.c[0]));
            dest->c[1] = max(0, min(255, col1.c[1] - col2.c[1]));
            dest->c[2] = max(0, min(255, col1.c[2] - col2.c[2]));
            break;
        case OP_MUL:
            dest->c[0] = max(0, min(255, col1.c[0] * col2.c[0]));
            dest->c[1] = max(0, min(255, col1.c[1] * col2.c[1]));
            dest->c[2] = max(0, min(255, col1.c[2] * col2.c[2]));
            break;
        case OP_DIV:
            dest->c[0] = max(0, min(255, (int32_t)col1.c[0] / (int32_t)col2.c[0]));
            dest->c[1] = max(0, min(255, (int32_t)col1.c[1] / (int32_t)col2.c[1]));
            dest->c[2] = max(0, min(255, (int32_t)col1.c[2] / (int32_t)col2.c[2]));
            break;
        case OP_MOD:
            dest->c[0] = max(0, min(255, (int32_t)col1.c[0] % (int32_t)col2.c[0]));
            dest->c[1] = max(0, min(255, (int32_t)col1.c[1] % (int32_t)col2.c[1]));
            dest->c[2] = max(0, min(255, (int32_t)col1.c[2] % (int32_t)col2.c[2]));
            break;
    }
    return 1;
}

//--

void s_comp_init(s_comp_t *self, s_source_t *col, generator_t *dist, int32_t index)
{
    self->method = s_comp_get;
    self->next = NULL; 
    self->col = col;
    self->dist = dist;
    self->index = index / SCALE_FACTOR;
}

uint8_t s_comp_get(void *_self, uint32_t t, color_t *dest)
{
    s_comp_t *self = (s_comp_t *)_self;
    int32_t h, s, v, dist;
    color_t col;
    
    dist = self->dist->method(self->dist, t);
    self->col->method(self->col, t, &col);

    if (self->index == 0)
    {
        dest->c[0] = col.c[0];
        dest->c[1] = col.c[1];
        dest->c[2] = col.c[2];
    }
    else
    if (self->index == 1)
    {
        rgb_to_hsv(&col, &h, &s, &v);
        h = (h - dist) % SCALE_FACTOR;
        if (h < 0)
            h += SCALE_FACTOR;
        hsv_to_rgb(h, s, v, dest);
    }
    else
    {
        rgb_to_hsv(&col, &h, &s, &v);
        h = (h + dist) % SCALE_FACTOR;
        hsv_to_rgb(h, s, v, dest);
    }
    return 1;
}
