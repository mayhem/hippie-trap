#ifndef __SOURCE_H__
#define __SOURCE_H__

#include "defs.h"
#include "generator.h"

void print_col(color_t *c);

uint8_t hsv_to_rgb(int32_t h, int32_t s, int32_t v, color_t *color);
uint8_t rgb_to_hsv(color_t *col, int32_t *_h, int32_t *_s, int32_t *_v);

typedef uint8_t (*s_method)(void *self, uint32_t t, color_t *col);

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
uint8_t s_constant_color_get(void *self, uint32_t t, color_t *dest);

typedef struct s_random_color_seq_t
{
    s_method   method;
    void      *next;
    int32_t    period;
    uint32_t   seed;
} s_random_color_seq_t;

void s_random_color_seq_init(s_random_color_seq_t *self, int32_t period, uint32_t seed);
uint8_t s_random_color_seq_get(void *self, uint32_t t, color_t *dest);

typedef struct s_hsv_t 
{ 
    s_method     method;
    void        *next; 
    generator_t *gen1;
    generator_t *gen2;
    generator_t *gen3;
} s_hsv_t;

void s_hsv_init(s_hsv_t *self, generator_t * gen1, generator_t *gen2, generator_t *gen3);
uint8_t s_hsv_get(void *self, uint32_t t, color_t *dest);

typedef struct s_rainbow_t 
{ 
    s_method     method;
    void        *next; 
    generator_t *gen;
} s_rainbow_t;

void s_rainbow_init(s_rainbow_t *self, generator_t *gen);
uint8_t s_rainbow_get(void *self, uint32_t t, color_t *dest);

typedef struct s_op_t 
{ 
    s_method     method;
    void        *next; 
    uint8_t      op;
    s_source_t  *s1, *s2;
} s_op_t;

void s_op_init(s_op_t *self, uint8_t op, s_source_t *s1, s_source_t *s2);
uint8_t s_op_get(void *self, uint32_t t, color_t *dest);

typedef struct s_comp_t 
{ 
    s_method     method;
    void        *next; 
    s_source_t  *col;
    generator_t *dist;
    int32_t      index;
} s_comp_t;

void s_comp_init(s_comp_t *self, s_source_t *col, generator_t *dist, int32_t index);
uint8_t s_comp_get(void *self, uint32_t t, color_t *dest);

typedef struct s_rgb_t 
{ 
    s_method     method;
    void        *next; 
    generator_t *red;
    generator_t *green;
    generator_t *blue;
} s_rgb_t;

void s_rgb_init(s_rgb_t *self, generator_t * red, generator_t *green, generator_t *blue);
uint8_t s_rgb_get(void *self, uint32_t t, color_t *dest);

#endif
