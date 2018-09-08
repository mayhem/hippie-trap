#include <stdlib.h>
#include <avr/pgmspace.h>
#include "defs.h"
#include "function.h"
#include "colorspace.h"

extern uint32_t  g_target;
extern uint32_t  g_global;
extern uint32_t  g_ticks_per_frame;
extern uint32_t  g_random_seed;
void set_pixel_color(uint8_t index, color_t *col);
void get_pixel_color(uint8_t index, color_t *col);

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
    static   color_t start_cols[NUM_LEDS], r_target;
    int32_t  delta_r, delta_g, delta_b;
    uint8_t  i;
    color_t  target, col, first_col;

    first_col.r = first_col.g = first_col.b = 0;

    // Save the current color if we're starting
    if (t == 0)
    {
        for(i = 0; i < NUM_LEDS; i++)
            get_pixel_color(i, &start_cols[i]);

        if (len == sizeof(uint16_t))
            hsv_to_rgb(rand() % SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR, &r_target);

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
        if (len == sizeof(uint16_t))
            target = r_target;
        else
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

        delta_r = (target.r - start_cols[i].r);
        delta_g = (target.g - start_cols[i].g);
        delta_b = (target.b - start_cols[i].b);

        int32_t step = t * SCALE_FACTOR / duration; 
        col.r = start_cols[i].r + (delta_r * step) / SCALE_FACTOR;
        col.g = start_cols[i].g + (delta_g * step) / SCALE_FACTOR;
        col.b = start_cols[i].b + (delta_b * step) / SCALE_FACTOR;

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
        hsv_to_rgb((offset + (250 * i) + (g_random_seed % SCALE_FACTOR)) % SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR, &col);
        set_pixel_color(i, &col);
    }
}

void p_decay(int32_t t, uint8_t *data, uint8_t len)
{
    int8_t divisor = *data, i;
    color_t col;

    if (t % divisor == 0)
        for(i = 0; i < NUM_LEDS; i++)
        {
            get_pixel_color(i, &col);
            col.r >>= 1;
            col.g >>= 1;
            col.b >>= 1;
            set_pixel_color(i, &col);
        }
}

/// Fast 16-bit approximation of sin(x). This approximation never varies more than
/// 0.69% from the floating point value you'd get by doing
///
///     float s = sin(x) * 32767.0;
///
/// @param theta input angle from 0-65535
/// @returns sin of theta, value between -32767 to 32767.
int16_t sin16_avr( uint16_t theta )
{
    static const uint8_t data[] =
    { 0,         0,         49, 0, 6393%256,   6393/256, 48, 0,
      12539%256, 12539/256, 44, 0, 18204%256, 18204/256, 38, 0,
      23170%256, 23170/256, 31, 0, 27245%256, 27245/256, 23, 0,
      30273%256, 30273/256, 14, 0, 32137%256, 32137/256,  4 /*,0*/ };

    uint16_t offset = (theta & 0x3FFF);

    // AVR doesn't have a multi-bit shift instruction,
    // so if we say "offset >>= 3", gcc makes a tiny loop.
    // Inserting empty volatile statements between each
    // bit shift forces gcc to unroll the loop.
    offset >>= 1; // 0..8191
    asm volatile("");
    offset >>= 1; // 0..4095
    asm volatile("");
    offset >>= 1; // 0..2047

    if( theta & 0x4000 ) offset = 2047 - offset;

    uint8_t sectionX4;
    sectionX4 = offset / 256;
    sectionX4 *= 4;

    uint8_t m;

    union {
        uint16_t b;
        struct {
            uint8_t blo;
            uint8_t bhi;
        };
    } u;

    //in effect u.b = blo + (256 * bhi);
    u.blo = data[ sectionX4 ];
    u.bhi = data[ sectionX4 + 1];
    m     = data[ sectionX4 + 2];

    uint8_t secoffset8 = (uint8_t)(offset) / 2;

    uint16_t mx = m * secoffset8;

    int16_t  y  = mx + u.b;
    if( theta & 0x8000 ) y = -y;

    return y;
}

const uint8_t sin_data_size = sizeof(int32_t) * 4;
// args: period, phase, amplitude, phase
void p_sine(int32_t t, uint8_t *data, uint8_t len)
{
    static  color_t orig_col[NUM_LEDS];
    color_t col;
    uint8_t i;

    int32_t period = *((int16_t *)data);
    data += sizeof(int16_t);
    int32_t amplitude = *((int16_t *)data);
    data += sizeof(uint16_t);
    int32_t phase = *((int16_t *)data);
    data += sizeof(int16_t);
    int32_t offset = *((int16_t *)data);
    data += sizeof(int16_t);

    if (t == 0)
    {
        if (len >= sin_data_size)
        {
            for(i = 0; i < NUM_LEDS; i++)
            {
                orig_col[i].r = *((uint8_t *)data);
                data += sizeof(uint8_t);
                orig_col[i].g = *((uint8_t *)data);
                data += sizeof(uint8_t);
                orig_col[i].b = *((uint8_t *)data);
                data += sizeof(uint8_t);
            }
        }
        else
        {
            get_pixel_color(0, &orig_col[0]);
            get_pixel_color(1, &orig_col[1]);
            get_pixel_color(2, &orig_col[2]);
            get_pixel_color(3, &orig_col[3]);
        }
    }

//    intensity = sin(t * period / SCALE_FACTOR + phase) * amplitude / SCALE_FACTOR + offset;
    int32_t intensity = sin(t);
    intensity /= 64;
    for(i = 0; i < NUM_LEDS; i++)
    {
        col.r = orig_col[i].r * intensity / SCALE_FACTOR;
        col.g = orig_col[i].g * intensity / SCALE_FACTOR;
        col.b = orig_col[i].b * intensity / SCALE_FACTOR;

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
        case 2:
            p_decay(t, data + 1, len - 1);
            break;
    }
}
