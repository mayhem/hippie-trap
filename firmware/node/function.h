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
typedef struct fu_function_t
{
    fu_method  method;
    void      *next;
} fu_function_t;

int32_t fu_local_random(int32_t lower, int32_t upper);

#endif
