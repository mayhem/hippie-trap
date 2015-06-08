#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <Arduino.h>

#include "source.h"
#include "filter.h"
#include "generator.h"

#define MAX_CODE_LEN           512
#define MAX_NUM_ARGS             8
#define VALUE_SIZE               4
#define ARG_VALUE                0
#define ARG_FUNC                 1
#define ARG_COLOR                2
#define ARG_BOTTLE_SUPPLIED      3

#define FILTER_FADE_IN           0
#define FILTER_FADE_OUT          1
#define FILTER_BRIGHTNESS        2
#define GEN_SIN                  3
#define GEN_SQUARE               4
#define GEN_SAWTOOTH             5
#define SRC_CONSTANT_COLOR       6
#define SRC_RAND_COL_SEQ         7
#define SRC_HSV                  8
#define SRC_RAINBOW              9
#define GEN_STEP                10

#define HEAP_SIZE              255

uint8_t heap[HEAP_SIZE];
uint16_t heap_offset = 0;

// TODO: Add heap protection function.
// set color coded debug errors: out of heap, failed to parse.
// allow for re-transmissions of patterns.
// send pattern
//    if I have a good pattern in memory, ignore new paterns.
//    go to next pattern: clean in pattern memory

void clear_heap(void)
{
    heap_offset = 0;
}

void *heap_alloc(uint8_t bytes)
{ 
    uint8_t *ptr = heap + heap_offset;
    if (bytes + heap_offset > HEAP_SIZE)
         return NULL;

    heap_offset += bytes;

    return ptr;
}

void *create_object(uint8_t id, 
                    int32_t  *values, uint8_t value_count,
                    void    **gens, uint8_t gen_count,
                    color_t  *colors, uint8_t color_count)
{
    void *obj = NULL;

    switch(id)
    {
        case FILTER_FADE_IN:
            {
                if (value_count == 2)
                {
                    obj = heap_alloc(sizeof(f_fade_in_t));
                    if (!obj)
                        return NULL;
                    f_fade_in_init((f_fade_in_t *)obj, f_fade_in_get, values[0], values[1]);
                }
                else
                    return NULL;
            }
            break;

        case FILTER_FADE_OUT:
            {
                if (value_count == 2)
                {
                    obj = heap_alloc(sizeof(f_fade_out_t));
                    if (!obj)
                        return NULL;
                    f_fade_out_init((f_fade_out_t *)obj, f_fade_out_get, values[0], values[1]);
                }
                else
                    return NULL;            
            }
            break;

        case FILTER_BRIGHTNESS:
            {
                if (gen_count == 1)
                {
                    obj = heap_alloc(sizeof(f_brightness_t));
                    if (!obj)
                        return NULL;
                    f_brightness_init((f_brightness_t *)obj, (generator_t*)gens[0]);
                }
                else
                    return NULL;            
            }
            break;

        case SRC_CONSTANT_COLOR:
            {
                if (color_count == 1)
                {
                    obj = heap_alloc(sizeof(s_constant_color_t));
                    if (!obj)
                        return NULL;
                    s_constant_color_init((s_constant_color_t *)obj, &colors[0]);
                }
                else
                    return NULL;            
            }
            break;

        case SRC_RAND_COL_SEQ:
            {
                if (value_count == 2)
                {
                    obj = heap_alloc(sizeof(s_random_color_seq_t));
                    if (!obj)
                        return NULL;
                    s_random_color_seq_init((s_random_color_seq_t *)obj, values[0], values[1]);
                }
                else
                    return NULL;            }
            break;

        case SRC_HSV:
            {
                if (gen_count > 1)
                {
                    obj = heap_alloc(sizeof(s_hsv_t));
                    if (!obj)
                        return NULL;
                    if (gen_count > 2)
                        s_hsv_init((s_hsv_t *)obj, (generator_t*)gens[0],  (generator_t*)gens[1],  (generator_t*)gens[2]);
                    else
                    if (gen_count > 1)
                        s_hsv_init((s_hsv_t *)obj,  (generator_t*)gens[0],  (generator_t*)gens[1], NULL);
                    else
                        s_hsv_init((s_hsv_t *)obj,  (generator_t*)gens[0], NULL, NULL);
                }
                else
                    return NULL;            
            }
            break;

        case SRC_RAINBOW:
            {
                if (gen_count == 1)
                {
                    obj = heap_alloc(sizeof(s_rainbow_t));
                    if (!obj)
                        return NULL;
                    s_rainbow_init((s_rainbow_t *)obj,  (generator_t*)gens[0]);
                }
                else
                    return NULL;            
            }
            break;

        case GEN_SIN:
        case GEN_SQUARE:
        case GEN_SAWTOOTH:
        case GEN_STEP:
            {
                if (value_count == 4)
                {
                    obj = heap_alloc(sizeof(generator_t));
                    if (!obj)
                        return NULL;
                    switch(id)
                    {
                        case GEN_SIN:
                            g_generator_init(obj, g_sin, values[0], values[1], values[2], values[3]);
                        break;
                        case GEN_SQUARE:
                            g_generator_init(obj, g_square, values[0], values[1], values[2], values[3]);
                        break;
                        case GEN_SAWTOOTH:
                            g_generator_init(obj, g_sawtooth, values[0], values[1], values[2], values[3]);
                        break;
                        case GEN_STEP:
                            g_generator_init(obj, g_step, values[0], values[1], values[2], values[3]);
                        break;
                    }
                }
                else
                    return NULL;
            }
            break;
    }
    return obj;
}

/*
| 1 byte   | 2 bytes  |
| ID - ARG | FUNC SIG | ( 
*/

void *parse_func(uint8_t *code, uint16_t len, uint16_t *index)
{
    uint8_t  id, num_args, i, arg, value_count = 0, gen_count = 0, color_count = 0;
    uint16_t arg_index;
    uint32_t args, value;
    int32_t  values[MAX_NUM_ARGS];
    void    *gens[MAX_NUM_ARGS];
    color_t  colors[MAX_NUM_ARGS];

    id = code[*index] >> 4;
    num_args = code[*index] & 0xF;

    args = (code[*index + 2] << 8) | code[*index + 1];
    arg_index = *index + 3;
    for(i = 0; i < num_args; i++)
    {
        arg = (args >> (i * 2)) & 0x3;
        if (arg == ARG_VALUE)
        {
            values[value_count++] = *((uint32_t *)&code[arg_index]); 
            arg_index += VALUE_SIZE;
        }
        else if (arg == ARG_FUNC)
        {
            gens[gen_count++] = parse_func(code, len, &arg_index);
        }
        else if (arg == ARG_COLOR)
        {
            colors[color_count].c[0] = code[arg_index++];
            colors[color_count].c[1] = code[arg_index++];
            colors[color_count++].c[2] = code[arg_index++];
        }
        else
            return NULL;
    }
    *index = arg_index;

    return create_object(id, values, value_count, gens, gen_count, colors, color_count);
}

void *parse(uint8_t *code, uint16_t len)
{
    void       *source, *ptr, *filter;
    uint16_t    offset = 0;

    clear_heap();
    source = parse_func(code, len, &offset);
    for(; offset < len;)
    {
        filter = parse_func(code, len, &offset);
        if (!filter)
            return NULL;

        ptr = (s_source_t *)source;
        while (((f_filter_t *)ptr)->next)
            ptr = ((f_filter_t *)ptr)->next;

        ((f_filter_t *)ptr)->next = filter;
    }

    return source;
}

void evaluate(s_source_t *src, uint32_t t, color_t *color)
{
    color_t  temp, dest;
    void    *filter;

    src->method((void *)src, t, &dest);
    filter = src->next;
    while(filter)
    {
        temp.c[0] = dest.c[0];
        temp.c[1] = dest.c[1];
        temp.c[2] = dest.c[2];
        ((f_filter_t *)filter)->method(filter, t, &temp, &dest);

        filter = ((f_filter_t *)filter)->next;
    }
    color->c[0] = dest.c[0];
    color->c[1] = dest.c[1];
    color->c[2] = dest.c[2];
}

