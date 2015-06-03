#ifndef __SOURCE_H__
#define __SOURCE_H__

#include "defs.h"

typedef struct s_constant_color_t
{
    void     (*method)(struct s_constant_color_t *self, uint32_t t, color_t *col);
    color_t    color;
    void      *next;
} s_constant_color_t;

void s_constant_color_init(s_constant_color_t *self, color_t *color);
void s_constant_color_get(s_constant_color_t *self, uint32_t t, color_t *dest);

typedef struct s_random_color_seq_t
{
    void     (*method)(struct s_random_color_seq_t *self, uint32_t t, color_t *col);
    int32_t    period;
    uint32_t   seed;
    void      *next;
} s_random_color_seq_t;

void s_random_color_seq_init(s_random_color_seq_t *self, int32_t period, uint32_t seed);
void s_random_color_seq_get(s_random_color_seq_t *self, uint32_t t, color_t *dest);
#endif
