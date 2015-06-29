#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <Arduino.h>

#include "source.h"
#include "filter.h"
#include "function.h"
#include "generator.h"
#include "parse.h"

#define MAX_NUM_ARGS             8
#define VALUE_SIZE               4
#define ARG_VALUE                0
#define ARG_FUNC                 1
#define ARG_COLOR                2
#define ARG_SRC                  3

#define LOCAL_ID                 0
#define LOCAL_POS_X              2
#define LOCAL_POS_Y              3
#define LOCAL_POS_Z              4

#define FILTER_FADE_IN              0
#define FILTER_FADE_OUT             1
#define FILTER_BRIGHTNESS           2
#define GEN_SIN                     3
#define GEN_SQUARE                  4
#define GEN_SAWTOOTH                5
#define SRC_CONSTANT_COLOR          6
#define SRC_RAND_COL_SEQ            7
#define SRC_HSV                     8
#define SRC_RAINBOW                 9
#define GEN_STEP                   10
#define FUNC_SPARKLE               11
#define FUNC_GENOP                 12
#define FUNC_SRCOP                 13
#define FUNC_ABS                   14
#define GEN_LINE                   15
#define GEN_CONSTANT               16
#define FUNC_COMPLEMENTARY         17
#define FUNC_LOCAL_RANDOM          18
#define GEN_IMPULSE                19
#define FUNC_REPEAT_LOCAL_RANDOM   20
#define SRC_CONSTANT_RANDOM_COLOR  21
#define FUNC_COLOR_SHIFT           22
#define SRC_RGB                    23

int32_t master_brightness = 1000;

// variables to help manage the heap.
uint8_t *cur_heap = NULL;
uint16_t heap_offset = 0;

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

void *create_object(uint8_t   id, uint8_t *is_local,
                    int32_t  *values, uint8_t value_count,
                    void    **gens, uint8_t gen_count,
                    color_t  *colors, uint8_t color_count)
{
    void *obj = NULL;

    *is_local = 0;
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
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
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
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
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
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
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
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;

        case SRC_CONSTANT_RANDOM_COLOR:
            {
                if (value_count == 3)
                {
                    color_t col;

                    obj = heap_alloc(sizeof(s_constant_color_t));
                    if (!obj)
                        return NULL;

                    hsv_to_rgb(values[0], values[1], values[2], &col);
                    s_constant_color_init((s_constant_color_t *)obj, &col);
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
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
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;

        case SRC_HSV:
            {
                
                if (gen_count > 0)
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
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;

        case SRC_RGB:
            {
                if (gen_count > 0)
                {
                    obj = heap_alloc(sizeof(s_rgb_t));
                    if (!obj)
                        return NULL;
                           
                    if (gen_count > 2)
                        s_rgb_init((s_rgb_t *)obj, (generator_t*)gens[0],  (generator_t*)gens[1],  (generator_t*)gens[2]);
                    else
                    if (gen_count > 1)
                        s_rgb_init((s_rgb_t *)obj,  (generator_t*)gens[0],  (generator_t*)gens[1], NULL);
                    else
                        s_rgb_init((s_rgb_t *)obj,  (generator_t*)gens[0], NULL, NULL);  
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
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
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;

        case FUNC_COMPLEMENTARY:
            {
                if (value_count == 1 && gen_count == 2)
                {
                    obj = heap_alloc(sizeof(s_comp_t));
                    if (!obj)
                        return NULL;
                    s_comp_init((s_comp_t *)obj, (s_source_t *)gens[0], (generator_t *)gens[1], values[0]);
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;
        
        case GEN_SQUARE:
            {
                if (value_count == 5)
                {
                    obj = heap_alloc(sizeof(square_t));
                    if (!obj)
                        return NULL;

                    g_square_init(obj, g_square, values[0], values[1], values[2], values[3], values[4]);
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;
                     
        case GEN_SIN:
            {
                if (value_count == 4)
                {
                    obj = heap_alloc(sizeof(generator_t));
                    if (!obj)
                        return NULL;

                    g_sin_init(obj, g_sin, values[0], values[1], values[2], values[3]);
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;  
            
        case GEN_SAWTOOTH:
            {
                if (value_count == 4)
                {
                    obj = heap_alloc(sizeof(generator_t));
                    if (!obj)
                        return NULL;

                    g_sawtooth_init(obj, g_sawtooth, values[0], values[1], values[2], values[3]);
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;  
            
        case GEN_STEP:
        case GEN_LINE:
        case GEN_IMPULSE:
            {
                if (value_count == 4)
                {
                    obj = heap_alloc(sizeof(generator_t));
                    if (!obj)
                        return NULL;
                    switch(id)
                    {
                        case GEN_STEP:
                            g_generator_init(obj, g_step, values[0], values[1], values[2], values[3]);
                        break;
                        case GEN_LINE:
                            g_generator_init(obj, g_line, values[0], values[1], values[2], values[3]);
                        break;
                        case GEN_IMPULSE:
                            g_generator_init(obj, g_impulse, values[0], values[1], values[2], values[3]);
                        break;
                    }
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;

        case FUNC_GENOP:
            {
                if (value_count == 1 && gen_count == 2)
                {
                    obj = heap_alloc(sizeof(s_op_t));
                    if (!obj)
                        return NULL;
                    g_generator_op_init(obj, (uint8_t)values[0], (generator_t*)gens[0], (generator_t*)gens[1]);
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;

        case FUNC_SRCOP:
            {
                if (value_count == 1 && gen_count == 2)
                {
                    obj = heap_alloc(sizeof(s_op_t));
                    if (!obj)
                        return NULL;
                    s_op_init((s_op_t *)obj, (uint8_t)values[0], (s_source_t*)gens[0], (s_source_t*)gens[1]);
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;

        case FUNC_ABS:
            {
                if (gen_count == 1)
                {
                    obj = heap_alloc(sizeof(g_abs_t));
                    if (!obj)
                        return NULL;
                    g_abs_init(obj, (generator_t *)gens[0]);
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;

        case GEN_CONSTANT:
            {
                if (value_count == 1)
                {
                    obj = heap_alloc(sizeof(g_constant_t));
                    if (!obj)
                        return NULL;
                    g_constant_init((g_constant_t *)obj, values[0]);
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;
    
        case FUNC_LOCAL_RANDOM:
            {
                *is_local = 1;
                if (value_count == 2)
                {

                    int32_t ret = fu_local_random(values[0], values[1]);   
                    return (void *)ret;
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;
            
        case FUNC_REPEAT_LOCAL_RANDOM:
            {
                *is_local = 1;
                if (value_count == 1)
                {

                    int32_t ret = fu_repeat_local_random(values[0] / SCALE_FACTOR);
                    return (void *)ret;
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;         
         
        case FUNC_COLOR_SHIFT:
            {
                if (value_count == 3)
                {
                    obj = heap_alloc(sizeof(f_color_shift_t));
                    if (!obj)
                        return NULL;

                    f_color_shift_init((f_color_shift_t *)obj, values[0], values[1], values[2]);
                }
                else
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }
            }
            break;   
    }
    
    return obj;
}

/*
| 1 byte   | 2 bytes  |
| ID - ARG | FUNC SIG | ( 
*/

void *parse_func(uint8_t *code, uint16_t len, uint16_t *index, uint8_t *is_local)
{
    uint8_t  id, num_args, i, arg, value_count = 0, gen_count = 0, color_count = 0;
    uint16_t arg_index;
    uint32_t args, value;
    int32_t  values[MAX_NUM_ARGS];
    void    *gens[MAX_NUM_ARGS], *ret;
    color_t  colors[MAX_NUM_ARGS];

    id = code[*index] >> 3;
    
    num_args = code[*index] & 0x7;

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
            uint8_t local = 0;
            gens[gen_count++] = parse_func(code, len, &arg_index, &local);
            if (local)
            {
                gen_count--;
                values[value_count++] = (uint32_t)gens[gen_count];
            }
        }
        else if (arg == ARG_COLOR)
        {
            colors[color_count].c[0] = code[arg_index++];
            colors[color_count].c[1] = code[arg_index++];
            colors[color_count++].c[2] = code[arg_index++];
        }
        else
        if (arg == ARG_SRC)
        {
            uint8_t  local, i, filter_count = code[arg_index++];
            void    *ptr, *filter;
            
            gens[gen_count] = parse_func(code, len, &arg_index, &local);
            
            for(i = 0; i < filter_count; i++)
            {
                filter = parse_func(code, len, &arg_index, &local);
                if (!filter)
                {
                    g_error = ERR_PARSE_FAILURE;
                    return NULL;
                }

                ptr = (s_source_t *)gens[gen_count];
                while (((f_filter_t *)ptr)->next)
                    ptr = ((f_filter_t *)ptr)->next;

                ((f_filter_t *)ptr)->next = filter;
            }
            gen_count++;
        }
    }
    *index = arg_index;

    void *r = create_object(id, is_local, values, value_count, gens, gen_count, colors, color_count);
    return r;
}

void *parse(uint8_t *code, uint16_t len, uint8_t *heap)
{
    void       *source, *filter, *ptr;
    uint16_t    offset = 0;
    uint8_t     local;

    heap_setup(heap);
    clear_local_random_values();
    
    source = parse_func(code, len, &offset, &local);
    if (!source)
        return NULL;
        
    for(; offset < len;)
    {
        
        filter = parse_func(code, len, &offset, &local);
        if (!filter)
            return NULL;
       
        ptr = (s_source_t *)source;
        while (((f_filter_t *)ptr)->next)
            ptr = ((f_filter_t *)ptr)->next;

        ((f_filter_t *)ptr)->next = filter;
    }

    return source;
}

uint8_t evaluate(s_source_t *src, uint32_t _t, color_t *color)
{
    uint32_t t;
    color_t  dest;
    
    t = (_t * g_speed) / SCALE_FACTOR;
    if (!sub_evaluate(src, t, &dest))
        return 0;

    color->c[0] = dest.c[0] * master_brightness / SCALE_FACTOR;
    color->c[1] = dest.c[1] * master_brightness / SCALE_FACTOR;
    color->c[2] = dest.c[2] * master_brightness / SCALE_FACTOR;
    
    return 1;
}

uint8_t sub_evaluate(s_source_t *src, uint32_t t, color_t *color)
{
    color_t  temp, dest;
    void    *filter;

    if (!src->method((void *)src, t, &dest))
        return 0;

    filter = src->next;
    while(filter)
    {
        temp.c[0] = dest.c[0];
        temp.c[1] = dest.c[1];
        temp.c[2] = dest.c[2];
        if (!((f_filter_t *)filter)->method(filter, t, &temp, &dest))
            return 0;

        filter = ((f_filter_t *)filter)->next;
    }
    color->c[0] = dest.c[0];
    color->c[1] = dest.c[1];
    color->c[2] = dest.c[2];

    return 1;
}

void set_brightness(int32_t brightness)
{
    master_brightness = brightness;
}
