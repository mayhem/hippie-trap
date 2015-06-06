#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "source.h"
#include "filter.h"
#include "generator.h"

#define MAX_CODE_LEN      512
#define MAX_NUM_ARGS        8
#define VALUE_SIZE          4
#define ARG_VALUE           0
#define ARG_FUNC            1
#define ARG_COLOR           2
#define ARG_BOTTLE_SUPPLIED 3

#define FUNC_FADE_IN           0
#define FUNC_FADE_OUT          1
#define FUNC_BRIGHTNESS        2
#define FUNC_SIN               3
#define FUNC_SQUARE            4
#define FUNC_SAWTOOTH          5
#define FUNC_CONSTANT_COLOR    6
#define FUNC_RAND_COL_SEQ      7
#define FUNC_HSV               8
#define FUNC_RAINBOW           9
#define FUNC_STEP              10

#define HEAP_SIZE              256

uint8_t heap[HEAP_SIZE];
uint8_t heap_offset = 0;

void clear_heap(void)
{
    heap_offset = 0;
}

void *heap_alloc(uint8_t bytes)
{ 
    printf("heap: alloc %d bytes\n", bytes);
    uint8_t *ptr = heap + heap_offset;
    if (bytes + heap_offset > HEAP_SIZE)
    {
        fprintf(stderr, "Out of heap space!\n");
        exit(-1);
    }

    heap_offset += bytes;

    return ptr;
}

void *create_object(uint8_t id, 
                    int32_t  *values, uint8_t value_count,
                    void    **gens, uint8_t gen_count,
                    color_t  *colors, uint8_t color_count)
{
    void *obj = NULL;

    printf("Create object: %d\n", id);
    switch(id)
    {
        case FUNC_FADE_IN:
            {
                if (value_count == 2)
                {
                    obj = heap_alloc(sizeof(f_fade_in_t));
                    f_fade_in_init((f_fade_in_t *)obj, f_fade_in_get, values[0], values[1]);
                }
            }
            break;

        case FUNC_FADE_OUT:
            {
                if (value_count == 2)
                {
                    printf("create func fade out: %d %d\n", values[0], values[1]);
                    obj = heap_alloc(sizeof(f_fade_out_t));
                    f_fade_out_init((f_fade_out_t *)obj, f_fade_out_get, values[0], values[1]);
                }
            }
            break;

        case FUNC_BRIGHTNESS:
            {
                if (gen_count == 1)
                {
                    obj = heap_alloc(sizeof(f_brightness_t));
                    f_brightness_init((f_brightness_t *)obj, f_brightness_get, gens[0]);
                }
            }
            break;

        case FUNC_CONSTANT_COLOR:
            {
                if (color_count == 1)
                {
                    obj = heap_alloc(sizeof(s_constant_color_t));
                    s_constant_color_init((s_constant_color_t *)obj, &colors[0]);
                }
            }
            break;

        case FUNC_RAND_COL_SEQ:
            {
                if (value_count == 2)
                {
                    obj = heap_alloc(sizeof(s_random_color_seq_t));
                    s_random_color_seq_init((s_random_color_seq_t *)obj, values[0], values[1]);
                }
            }
            break;

        case FUNC_HSV:
            {
                if (gen_count > 1)
                {
                    obj = heap_alloc(sizeof(s_hsv_t));
                    if (gen_count > 2)
                        s_hsv_init((s_hsv_t *)obj, gens[0], gens[1], gens[2]);
                    else
                    if (gen_count > 1)
                        s_hsv_init((s_hsv_t *)obj, gens[0], gens[1], NULL);
                    else
                        s_hsv_init((s_hsv_t *)obj, gens[0], NULL, NULL);
                }
            }
            break;

        case FUNC_RAINBOW:
            {
                if (gen_count == 1)
                {
                    obj = heap_alloc(sizeof(s_rainbow_t));
                    s_rainbow_init((s_rainbow_t *)obj, gens[0]);
                }
            }
            break;

        case FUNC_SIN:
        case FUNC_SQUARE:
        case FUNC_SAWTOOTH:
        case FUNC_STEP:
            {
                if (value_count == 4)
                {
                    obj = heap_alloc(sizeof(generator_t));
                    switch(id)
                    {
                        case FUNC_SIN:
                            g_generator_init(obj, g_sin, values[0], values[1], values[2], values[3]);
                        break;
                        case FUNC_SQUARE:
                            g_generator_init(obj, g_square, values[0], values[1], values[2], values[3]);
                        break;
                        case FUNC_SAWTOOTH:
                            g_generator_init(obj, g_sawtooth, values[0], values[1], values[2], values[3]);
                        break;
                        case FUNC_STEP:
                            g_generator_init(obj, g_step, values[0], values[1], values[2], values[3]);
                        break;
                    }
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

void *parse_func(char *code, int16_t len, uint16_t *index)
{
    uint8_t  id, num_args, i, arg, value_count = 0, gen_count = 0, color_count = 0;
    uint16_t arg_index;
    uint32_t args, value;
    int32_t  values[MAX_NUM_ARGS];
    void    *gens[MAX_NUM_ARGS];
    color_t  colors[MAX_NUM_ARGS];

    id = code[*index] >> 4;
    num_args = code[*index] & 0xF;

    printf("id %d args %d\n", id, num_args);

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
            printf("  unknown ");
    }
    *index = arg_index;

    return create_object(id, values, value_count, gens, gen_count, colors, color_count);
}

void *parse(char *code, int16_t len)
{
    void       *source, *ptr, *filter;
    uint16_t    offset = 0;

    clear_heap();
    source = parse_func(code, len, &offset);
    for(; offset < len;)
    {
        filter = parse_func(code, len, &offset);
        if (!filter)
            break;

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
        f_filter_t *foo = (f_filter_t *)filter;
        foo->method(filter, t, &temp, &dest);
//        ((f_filter_t *)filter)->method(filter, t, &temp, &dest);

        filter = ((f_filter_t *)filter)->next;
    }
    color->c[0] = dest.c[0];
    color->c[1] = dest.c[1];
    color->c[2] = dest.c[2];
}

int main(int argc, char *argv[])
{
    FILE          *fp;
    uint16_t       rd, index = 0;
    char           code[MAX_CODE_LEN], pair[3];
    unsigned int   ch;
    s_source_t    *source;
    color_t        color;
    uint32_t       t;

    if (argc < 2)
    {
        printf("parse <bin file>\n");
        exit(-1);
    }
    fp = fopen(argv[1], "rb");
    if (!fp)
    {
        printf("Cannot open %s\n", argv[1]);
        exit(-1);
    }
    pair[2] = 0;
    for(index = 0;; index++)
    {
        rd = fread(pair, 1, 2, fp);
        if (rd < 2)
            break;
        sscanf(pair, "%02X", &ch);
        code[index] = ch;
        printf("%02X ", ch);
    }
    printf("\n");

    source = parse(code, index);
    if (!source)
    {
        printf("Parse failed.\n");
        return 0;
    }

    for(t = 0; t < SCALE_FACTOR * 6; t += 100)
//    t = 0;
    {
        evaluate(source, t, &color);
        printf("%u: %d, %d, %d\n", t, color.c[0], color.c[1], color.c[2]);
    }

    return 0;
}
