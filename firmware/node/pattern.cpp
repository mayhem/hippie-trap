#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <avr/pgmspace.h>

#include "serial.h"
#include "function.h"
#include "pattern.h"

int32_t master_brightness = 1000;


#define DEFAULT_PERIOD      1.0
#define DEFAULT_PHASE       0.0
#define DEFAULT_AMPLITUDE   1.0
#define DEFAULT_OFFSET      0.0

/*

   Wire protocol

function
========

[type          8 bits ]
[arg count     4 bits 
 dest          4 bits ]
    [ arg       32 bytes ]

WIRE PROTOCOL

[number of func    8 bits  ]
[period            4 bytes ]
[function 0        ? bytes ]


...
[function n        ? bytes ]

*/

// Reserve space for the patterns
uint8_t g_pattern_heap[2][HEAP_SIZE];
uint16_t g_pattern_heap_offset[2];

void func_alloc_setup(uint8_t pattern_index)
{
    g_pattern_heap_offset[pattern_index] = 0;
}

function_t *func_alloc(uint8_t pattern_index, uint8_t type, uint8_t dest, uint8_t arg_count, uint8_t bytes)
{ 
    uint8_t *ptr = g_pattern_heap[pattern_index] + g_pattern_heap_offset[pattern_index];

    g_pattern_heap_offset[pattern_index] += bytes;
    if (g_pattern_heap_offset[pattern_index] >= HEAP_SIZE)
    {
        set_error(ERR_OUT_OF_HEAP);
        return NULL;
    }

    function_t *func = (function_t *)ptr;
    func->type = type;
    func->dest = dest;
    func->arg_count = arg_count;

    return func;
}

function_t *create_func(uint8_t pattern_index, uint8_t type, uint8_t dest, uint8_t arg_count, uint32_t *args)
{
    function_t *obj;

    switch(type)
    {
        case FUNCTION_NONE:
            return NULL;

        case FUNCTION_ERROR:
            {
                obj = func_alloc(pattern_index, type, dest, arg_count, sizeof(function_t));
                if (!obj)
                    return NULL;

                return obj;
            }
            break;

        case FUNCTION_SQUARE:
            {
                if (arg_count != 5)
                {
                    set_error(ERR_PARSE_FAILURE);
                    return NULL;
                }
 
                obj = func_alloc(pattern_index, type, dest, arg_count, sizeof(square_t));
                if (!obj)
                    return NULL;

                f_square_init(obj, args[0], args[1], args[2], args[3], args[4]);

                return obj;
            }
            break;
    }
                     
    return NULL;
}

void setup_error_pattern(void)
{
    pattern_t *pattern = &g_patterns[0];

    memset(pattern, 0, sizeof(pattern_t));
    func_alloc_setup(0);

    pattern->num_funcs = 1;
    pattern->period = 1000;
    pattern->functions[0] = create_func(0, FUNCTION_ERROR, DEST_LED_0, 0, NULL);
}

uint8_t parse_pattern(uint8_t pattern_index, uint8_t *code, uint16_t len)
{
    uint8_t  i, j, *index;
    pattern_t      *pattern = &g_patterns[pattern_index];

    memset(pattern, 0, sizeof(pattern_t));

    pattern->num_funcs = code[0];
    pattern->period = *(uint32_t *)&code[1];

    func_alloc_setup(pattern_index);

    index = &code[5];
    for(i = 0; i < pattern->num_funcs; i++)
    {
        function_t  *temp;
        uint8_t      type, arg_count, dest;
        uint32_t     args[MAX_ARGS];

        type = *index;
        index++;

        arg_count = *index & 0xF;
        dest = *index >> 4;
        index++;

        for(j = 0; j < arg_count; j++)
        {
            args[j] = *(uint32_t *)index;
            index += sizeof(int32_t);
        }

        // create function object here
        temp = create_func(pattern_index, type, dest, arg_count, args); 
        if (!temp)
            return 0;

        if (dest <= DEST_LED_11)
            pattern->functions[dest] = temp;
        else
            switch(dest)
            {
                case DEST_ALL:
                {
                    for(j = 0; j < 12; j++)
                        pattern->functions[j] = temp;
                    break;
                }
                case DEST_ALL_RED:
                {
                    pattern->functions[0] = temp;
                    pattern->functions[3] = temp;
                    pattern->functions[6] = temp;
                    pattern->functions[9] = temp;
                    break;
                }
                case DEST_ALL_GREEN:
                {
                    pattern->functions[1] = temp;
                    pattern->functions[4] = temp;
                    pattern->functions[7] = temp;
                    pattern->functions[10] = temp;
                    break;
                }
                case DEST_ALL_BLUE:
                {
                    pattern->functions[2] = temp;
                    pattern->functions[5] = temp;
                    pattern->functions[8] = temp;
                    pattern->functions[11] = temp;
                    break;
                }
            }
    }
    return 1;
}

uint8_t evaluate_function(function_t *function, uint32_t t, uint8_t *color)
{
    switch(function->type)
    {
        case FUNCTION_NONE:
            return 0;

        case FUNCTION_ERROR:
            *color = f_error(function, t);
            return 1;

        case FUNCTION_SQUARE:
            *color = f_square(function, t);
            return 1;

        default:
            return 0;
    }
}

void evaluate(pattern_t *pattern, uint32_t _t, uint8_t led, color_t *color)
{
    uint8_t  i, value, *ptr = (uint8_t *)color;
    uint32_t t;
   
    t = (_t * g_speed) / SCALE_FACTOR;
    for(i = 0; i < 3; i++, ptr++)
    {
        uint8_t findex = (led * 3) + i;
        if (pattern->functions[findex] && evaluate_function(pattern->functions[findex], t, &value))
            *ptr = value;
    }
}
