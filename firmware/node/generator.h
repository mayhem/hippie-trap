#ifndef __GENERATOR_H__
#define __GENERATOR_H__

#include <stdio.h>
#include <math.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include "defs.h"

#include "sin_table.h"

typedef int32_t (*g_method)(void *gen, uint32_t t);

typedef struct generator_t
{
    g_method    method;
    int32_t     period;
    int32_t     phase;
    int32_t     amplitude;
    int32_t     offset;
} generator_t;

typedef struct square_t
{
    g_method    method;
    int32_t     period;
    int32_t     phase;
    int32_t     amplitude;
    int32_t     offset;
    int32_t     duty;
} square_t;

void g_generator_init(void *self, g_method method, int32_t period, int32_t phase, int32_t amplitude, int32_t offset);
void g_square_init(void *self, g_method method, int32_t period, int32_t phase, int32_t amplitude, int32_t offset, int32_t duty);
void g_sin_init(void *self, g_method method, int32_t period, int32_t phase, int32_t amplitude, int32_t offset);
void g_sawtooth_init(void *self, g_method method, int32_t period, int32_t phase, int32_t amplitude, int32_t offset);

int32_t g_sin(void *self, uint32_t t);
int32_t g_square(void *self, uint32_t t);
int32_t g_sawtooth(void *self, uint32_t t);
int32_t g_step(void *self, uint32_t t);
int32_t g_line(void *self, uint32_t t);
int32_t g_impulse(void *self, uint32_t t);

const uint8_t OP_ADD = 0;
const uint8_t OP_SUB = 1;
const uint8_t OP_MUL = 2;
const uint8_t OP_DIV = 3;
const uint8_t OP_MOD = 4;

typedef struct generator_op_t
{
    g_method    method;
    generator_t *g, *g2;
    int8_t       op;
} generator_op_t;

void g_generator_op_init(void *self, uint8_t op, generator_t *g, generator_t *g2);
int32_t g_generator_op_get(void *self, uint32_t t);

typedef struct g_abs_t
{
    g_method     method;
    void        *next;
    generator_t *g;
} g_abs_t;

void g_abs_init(void *self, generator_t *g);
int32_t g_abs_get(void *_self, uint32_t t);

typedef struct g_constant_t
{
    g_method     method;
    void        *next;
    int32_t      value;
} g_constant_t;

void g_constant_init(void *self, int32_t value);
int32_t g_constant_get(void *_self, uint32_t t);

#endif
