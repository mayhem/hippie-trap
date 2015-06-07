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

void g_generator_init(void *self, g_method method, int32_t period, int32_t phase, int32_t amplitude, int32_t offset);
int32_t g_sin(void *self, uint32_t t);
int32_t g_square(void *self, uint32_t t);
int32_t g_sawtooth(void *self, uint32_t t);
int32_t g_step(void *self, uint32_t t);

#endif
