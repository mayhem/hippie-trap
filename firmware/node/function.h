#ifndef __FUNCTION_H__
#define __FUNCTION_H__

#include <stdio.h>
#include <math.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include "defs.h"

#include "sin_table.h"

// LED "destinations" 
#define DEST_LED_0          0
#define DEST_LED_1          1
#define DEST_LED_2          2
#define DEST_LED_3          3
#define DEST_LED_4          4
#define DEST_LED_5          5
#define DEST_LED_6          6
#define DEST_LED_7          7
#define DEST_LED_8          8
#define DEST_LED_9          9
#define DEST_LED_10        10
#define DEST_LED_11        10
#define DEST_ALL           12
#define DEST_ALL_RED       13 
#define DEST_ALL_BLUE      14
#define DEST_ALL_GREEN     15

#define FUNCTION_NONE       0
#define FUNCTION_SQUARE     1

typedef struct function_t
{
    uint8_t       type;
    uint8_t       arg_count;
    uint8_t       dest;
    void         *object;
} function_t;

typedef struct pattern_t
{
    uint8_t      num_funcs;
    uint32_t     period;
    function_t functions[NUM_PIXELS * 3];
} pattern_t;

typedef struct f_generator_t
{
    int32_t     period;
    int32_t     phase;
    int32_t     amplitude;
    int32_t     offset;
} generator_t;

typedef struct square_t
{
    int32_t     period;
    int32_t     phase;
    int32_t     amplitude;
    int32_t     offset;
    int32_t     duty;
} square_t;

void f_generator_init(void *self, int32_t period, int32_t phase, int32_t amplitude, int32_t offset);
void f_square_init(void *self, int32_t period, int32_t phase, int32_t amplitude, int32_t offset, int32_t duty);
void f_sin_init(void *self, int32_t period, int32_t phase, int32_t amplitude, int32_t offset);
void f_sawtooth_init(void *self, int32_t period, int32_t phase, int32_t amplitude, int32_t offset);

int32_t f_sin(void *self, int32_t t);
int32_t f_square(void *self, int32_t t);
int32_t f_sawtooth(void *self, int32_t t);
int32_t f_step(void *self, int32_t t);
int32_t f_line(void *self, int32_t t);
int32_t f_impulse(void *self, int32_t t);

#endif
