#ifndef __SOURCE_H__
#define __SOURCE_H__

#include "defs.h"
#include "generator.h"

void hsv_to_rgb(int32_t h, int32_t s, int32_t v, color_t *color);
void rgb_to_hsv(color_t *col, int32_t *_h, int32_t *_s, int32_t *_v);

typedef void (*s_method)(void *self, uint32_t t, color_t *col);

// IMPORTANT: All of the s_ structs below must follow the pattern of this struct below. Call it a base "class"!
typedef struct s_source_t
{
    s_method   method;
    void      *next;
} s_source_t;

typedef struct s_constant_color_t
{
    s_method   method;
    void      *next;
    color_t    color;
} s_constant_color_t;

void s_constant_color_init(s_constant_color_t *self, color_t *color);
void s_constant_color_get(void *self, uint32_t t, color_t *dest);

typedef struct s_random_color_seq_t
{
    s_method   method;
    void      *next;
    int32_t    period;
    uint32_t   seed;
} s_random_color_seq_t;

void s_random_color_seq_init(s_random_color_seq_t *self, int32_t period, uint32_t seed);
void s_random_color_seq_get(void *self, uint32_t t, color_t *dest);

typedef struct s_hsv_t 
{ 
    s_method     method;
    void        *next; 
    generator_t *gen1;
    generator_t *gen2;
    generator_t *gen3;
} s_hsv_t;

void s_hsv_init(s_hsv_t *self, generator_t * gen1, generator_t *gen2, generator_t *gen3);
void s_hsv_get(void *self, uint32_t t, color_t *dest);

typedef struct s_rainbow_t 
{ 
    s_method     method;
    void        *next; 
    generator_t *gen;
} s_rainbow_t;

void s_rainbow_init(s_rainbow_t *self, generator_t *gen);
void s_rainbow_get(void *self, uint32_t t, color_t *dest);

typedef struct s_op_t 
{ 
    s_method     method;
    void        *next; 
    uint8_t      op;
    s_source_t  *s1, *s2;
} s_op_t;

void s_op_init(s_op_t *self, uint8_t op, s_source_t *s1, s_source_t *s2);
void s_op_get(void *self, uint32_t t, color_t *dest);

typedef struct s_comp_t 
{ 
    s_method     method;
    void        *next; 
    color_t      col;
    int32_t      dist;
    int32_t      index;
} s_comp_t;

void s_comp_init(s_op_t *self, color_t *col, int32_t dist, int32_t index);
void s_comp_get(void *self, uint32_t t, color_t *dest);

#endif
