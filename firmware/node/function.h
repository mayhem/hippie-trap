#ifndef __FUNCTION_H__
#define __FUNCTION_H__

#include <stdio.h>
#include <math.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include "defs.h"


typedef void (*fu_method)(void *self, uint32_t t, int32_t *value);

// IMPORTANT: All of the f_ structs below must follow the pattern of this struct below. Call it a base "class"!
typedef struct f_function_t
{
    fu_method  method;
    void      *next;
} f_function_t;

typedef struct f_local_random_t
{
    fu_method  method;
    void      *next;
    int32_t    lower, upper, value;
} s_local_random_t;

void f_local_random_init(f_local_random_t *self, int32_t lower, int32_t upper);
void f_local_random_get(void *_self, uint32_t t, int32_t *dest);

#endif
