#ifndef __FILTER_H__
#define __FILTER_H__

#include <stdlib.h>
#include "generator.h"
#include "defs.h"

typedef void (*f_method)(void *self, uint32_t t, color_t *src, color_t *dest);

// IMPORTANT: All of the s_ structs below must follow the pattern of this struct below. Call it a base "class"!
typedef struct f_filter_t
{
    f_method   method;
    void      *next;
} f_filter_t;

typedef struct f_fade_in_t
{
    f_method   method;
    void      *next;
    int32_t    duration;
    int32_t    offset;
} f_fade_in_t;

void f_fade_in_init(f_fade_in_t *self, f_method method, int32_t duration, int32_t offset);
void f_fade_in_get(void *self, uint32_t t, color_t *src, color_t *dest);

typedef struct f_fade_out_t
{
    f_method   method;
    void      *next;
    int32_t    duration;
    int32_t    offset;
} f_fade_out_t;

void f_fade_out_init(f_fade_out_t *self, f_method method, int32_t duration, int32_t offset);
void f_fade_out_get(void *self, uint32_t t, color_t *src, color_t *dest);

typedef struct f_brightness_t
{
    f_method      method;
    void         *next;
    generator_t  *gen;
} f_brightness_t;

void f_brightness_init(f_brightness_t *self, generator_t *gen);
void f_brightness_get(void *self, uint32_t t, color_t *src, color_t *dest);

typedef struct f_color_shift_t
{
    f_method      method;
    void         *next;
    int32_t       h_shift, v_shift, s_shift;
} f_color_shift_t;

void f_color_shift_init(f_color_shift_t *self, int32_t h_shift, int32_t s_shift, int32_t v_shift);
void f_color_shift_get(void *self, uint32_t t, color_t *src, color_t *dest);

#endif
