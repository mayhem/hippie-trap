#include <Arduino.h>
#include <stdlib.h>
#include "source.h"
#include "pattern.h"
#include "defs.h"

#if 0
void print_col(color_t *c)
{
    Serial.print(c->c[0], DEC);
    Serial.print(", ");
    Serial.print(c->c[1], DEC);
    Serial.print(", ");
    Serial.print(c->c[2], DEC);
}
#endif

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
    
    *_h = h;
    *_s = s;
    *_v = v;

    return 1;
}


