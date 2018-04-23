#include <stdlib.h>
#include <avr/pgmspace.h>
#include "defs.h"
#include "function.h"
#include "colorspace.h"

extern uint32_t  g_target;
extern uint32_t  g_ticks_per_frame;
extern color_t  g_color[NUM_LEDS];
void set_pixel_color(uint8_t index, color_t *col);

void p_error(int32_t t, uint8_t *data, uint8_t len)
{
    color_t col;

    col.r = col.g = col.b = 0;
    if ((t / 2) % 2 == 0)
    {
        col.r = 128;
        set_pixel_color(1, &col);
        set_pixel_color(2, &col);
    }
    else
    {
        set_pixel_color(1, &col);
        set_pixel_color(2, &col);
    }
}

void p_fade_to(int32_t t, uint8_t *data, uint8_t len)
{
    static   color_t start_cols[NUM_LEDS];
    int32_t  h0, s0, v0, h1, s1, v1, delta_h, delta_s, delta_v;
    uint8_t  i;
    color_t  target, col, first_col;

    // Save the current color if we're starting
    if (t == 0)
    {
        for(i = 0; i < NUM_LEDS; i++)
            start_cols[i] = g_color[i];
        return;
    }

    int32_t duration = *((uint16_t *)data);
    data += sizeof(uint16_t);

    // If we're at the end of the pattern, bail
    if (t > duration)
    {
        g_target = 0;
        return;
    }

    for(i = 0; i < NUM_LEDS; i++)
    {
        if ((i * 3) < (len - sizeof(uint16_t)))
        {
            target.r = *((uint8_t *)data);
            data += sizeof(uint8_t);
            target.g = *((uint8_t *)data);
            data += sizeof(uint8_t);
            target.b = *((uint8_t *)data);
            data += sizeof(uint8_t);
        }
        else
            target = first_col;

        if (i == 0)
            first_col = target;

        rgb_to_hsv(&start_cols[i], &h0, &s0, &v0);
        rgb_to_hsv(&target, &h1, &s1, &v1);

        delta_h = (h1 - h0);
        delta_s = (s1 - s0);
        delta_v = (v1 - v0);

        int32_t step = t * SCALE_FACTOR / duration; 
        hsv_to_rgb(h0 + (delta_h * step) / SCALE_FACTOR, s0 + (delta_s * step) / SCALE_FACTOR, v0 + (delta_v * step) / SCALE_FACTOR, &col);
        set_pixel_color(i, &col);
    }
}

void p_rainbow(int32_t t, uint8_t *data, uint8_t len)
{
    int8_t divisor = *data, i;
    int32_t offset = t / divisor;
    color_t col;

    for(i = 0; i < NUM_LEDS; i++)
    {
        hsv_to_rgb((offset + (250 * i)) % SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR, &col);
        set_pixel_color(i, &col);
    }
}

void apply_pattern(int32_t t, uint8_t *data, uint8_t len)
{
    switch(*data)
    {
        case 0:
            p_fade_to(t, data + 1, len - 1);
            break;
        case 1:
            p_rainbow(t, data + 1, len - 1);
            break;
    }
}
