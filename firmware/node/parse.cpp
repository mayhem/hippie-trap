#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <Arduino.h>

#include "function.h"
#include "parse.h"

int32_t master_brightness = 1000;

// variables to help manage the heap.
uint8_t *cur_heap = NULL;
uint16_t heap_offset = 0;

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


void heap_setup(uint8_t *heap)
{
    heap_offset = 0;
    cur_heap = heap;
}

void *heap_alloc(uint8_t bytes)
{ 
    uint8_t *ptr = cur_heap + heap_offset;
    if (bytes + heap_offset > HEAP_SIZE)
    {
        g_error = ERR_OUT_OF_HEAP;
        return NULL;
    }

    heap_offset += bytes;

    return ptr;
}

void *create_object(uint8_t type, uint8_t dest, uint8_t arg_count, uint32_t *args)
{
    void     *obj;
            
    switch(type)
    {
        case FUNCTION_NONE:
            return NULL;

        case FUNCTION_SQUARE:
            {
                if (arg_count != 5)
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
 
                obj = heap_alloc(sizeof(square_t));
                if (!obj)
                    return NULL;

                f_square_init(obj, args[0], args[1], args[2], args[3], args[4]);

                return obj;
            }
            break;
    }
                     
    return NULL;
}

uint8_t parse_packet(uint8_t *code, uint16_t len, pattern_t *pattern)
{
    uint8_t  i, j, *index;

    memset(pattern, 0, sizeof(pattern_t));

    pattern->num_funcs = code[0];
    pattern->period = *(uint32_t *)&code[1];

    index = &code[5];
    for(i = 0; i < pattern->num_funcs; i++)
    {
        function_t temp;
        uint8_t      type, arg_count, dest;
        uint32_t args[MAX_ARGS];
        void     *obj;

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
        obj = create_object(type, dest, arg_count, args); 
        if (!obj)
            continue;

        if (pattern->functions[i].dest <= DEST_LED_11)
            pattern->functions[pattern->functions[i].dest].object = obj;
        else
            switch(pattern->functions[i].dest)
            {
                case DEST_ALL:
                {
                    for(j = 0; j < 12; j++)
                        pattern->functions[j].object = obj;
                    break;
                }
                case DEST_ALL_RED:
                {
                    pattern->functions[0].object = obj;
                    pattern->functions[3].object = obj;
                    pattern->functions[6].object = obj;
                    pattern->functions[9].object = obj;
                    break;
                }
                case DEST_ALL_GREEN:
                {
                    pattern->functions[1].object = obj;
                    pattern->functions[4].object = obj;
                    pattern->functions[7].object = obj;
                    pattern->functions[10].object = obj;
                    break;
                }
                case DEST_ALL_BLUE:
                {
                    pattern->functions[2].object = obj;
                    pattern->functions[5].object = obj;
                    pattern->functions[8].object = obj;
                    pattern->functions[11].object = obj;
                    break;
                }
            }
    }
}

uint8_t evaluate_function(function_t *function, uint32_t t, uint8_t *color)
{
    switch(function->type)
    {
        case FUNCTION_NONE:
            return 0;

        case FUNCTION_SQUARE:
            *color = f_square(function->object, t);
            return 1;
    }
}

uint8_t evaluate(pattern_t *pattern, uint32_t _t, uint8_t led, color_t *color)
{
    uint8_t  i, value;
    uint32_t t;
   
    t = (_t * g_speed) / SCALE_FACTOR;
    for(i = 0; i < 3; i++)
    {
        uint8_t findex = (led * 3) + i;
        if (evaluate_function(&pattern->functions[findex], t, &value))
            color->c[i] = value;
    }
}


