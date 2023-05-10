#include <stdlib.h>
#include <string.h>
#include <avr/pgmspace.h>
#include "defs.h"
#include "function.h"
#include "colorspace.h"

extern uint32_t  g_target;
extern uint32_t  g_global;
extern uint32_t  g_ticks_per_frame;
extern uint32_t  g_random_seed;
void set_led(uint8_t index, color_t *col);
void get_led(uint8_t index, color_t *col);
void adjust_led_brightness(uint8_t delta);
uint32_t ticks_to_ms(uint32_t ticks);
uint32_t ms_to_ticks(uint32_t ms);

void p_error(int32_t t, uint8_t *data, uint8_t len)
{
    color_t col;

    col.r = col.g = col.b = 0;
    if ((t / 2) % 2 == 0)
    {
        col.r = 128;
        set_led(1, &col);
        set_led(2, &col);
    }
    else
    {
        set_led(1, &col);
        set_led(2, &col);
    }
}

void p_fade_to(int32_t t, uint8_t *data, uint8_t len)
{
    static   color_t start_cols[NUM_LEDS], r_target[4];
    int32_t  delta_r, delta_g, delta_b;
    uint8_t  i, default_values, color_offset;
    color_t  target, col, first_col;

    first_col.r = first_col.g = first_col.b = 0;

    default_values = len == sizeof(uint16_t) + sizeof(uint8_t);
    color_offset = sizeof(uint16_t) + sizeof(uint8_t);
    int32_t duration_ms = *((uint16_t *)data);
    int32_t duration = ms_to_ticks(duration_ms);
    data += sizeof(uint16_t);
    uint8_t hue_shift = *((uint8_t *)data);
    data += sizeof(uint8_t);

    // Save the current color if we're starting
    if (t == 0)
    {
        for(i = 0; i < NUM_LEDS; i++)
            get_led(i, &start_cols[i]);

        if (default_values)
        {
            if (hue_shift == 0)
            {
                hsv_to_rgb(rand() % SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR, &r_target[0]);
                for(i = 1; i < NUM_LEDS; i++)
                    memcpy(&r_target[i], &r_target[0], sizeof(color_t));
            }
            else
                hueshift_to_rgb((uint32_t)hue_shift * SCALE_FACTOR / 255, rand() % SCALE_FACTOR,
                                 SCALE_FACTOR, SCALE_FACTOR, r_target);
        }

        return;
    }

    // If we're at the end of the pattern, bail
    if (t > duration)
    {
        g_target = 0;
        return;
    }

    for(i = 0; i < NUM_LEDS; i++)
    {
        if (default_values)
            target = r_target[i];
        else
        if ((i * 3) < (len - color_offset))
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

        delta_r = (target.r - start_cols[i].r);
        delta_g = (target.g - start_cols[i].g);
        delta_b = (target.b - start_cols[i].b);

        int32_t step = t * SCALE_FACTOR / duration; 
        col.r = start_cols[i].r + (delta_r * step) / SCALE_FACTOR;
        col.g = start_cols[i].g + (delta_g * step) / SCALE_FACTOR;
        col.b = start_cols[i].b + (delta_b * step) / SCALE_FACTOR;

        set_led(i, &col);
    }
}

void p_rainbow(int32_t t, uint8_t *data, uint8_t len)
{
    int8_t divisor = *data, i;
    int32_t offset = t / divisor;
    color_t col;

    for(i = 0; i < NUM_LEDS; i++)
    {
        hsv_to_rgb((offset + (250 * i) + (g_random_seed % SCALE_FACTOR)) % SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR, &col);
        set_led(i, &col);
    }
}

void p_decay(int32_t t, uint8_t *data, uint8_t len)
{
    int8_t decr = *data;
    adjust_led_brightness(decr);
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
        case 2:
            p_decay(t, data + 1, len - 1);
            break;
    }
}
