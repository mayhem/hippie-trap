#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "source.h"
#include "filter.h"

#define MAX_CODE_LEN      512
#define MAX_NUM_ARGS        8
#define VALUE_SIZE          2
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

/*
| 1 byte   | 2 bytes  |
| ID - ARG | FUNC SIG | ( 
*/

void *parse_func(char *code, int16_t len, uint16_t *index)
{
    uint8_t  id, num_args, i, arg, value_count = 0, gen_count = 0, color_count = 0;
    uint16_t args, arg_index, value;
    int32_t  values[MAX_NUM_ARGS];
    void    *gens[MAX_NUM_ARGS];
    color_t  colors[MAX_NUM_ARGS];

    if (*index == 0)
        clear_heap();

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
            values[value_count++] = *((uint16_t *)&code[arg_index]); 
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

    switch(id)
    {
        case FUNC_FADE_IN:
            {
                if (value_count == 2)
                {
                    f_fade_in_t *obj = heap_alloc(sizeof(f_fade_in_t));
                    f_fade_in_init(obj, values[0], values[1]);
                }
            }
            break;

        case FUNC_FADE_OUT:
            {
                if (value_count == 2)
                {
                    f_fade_out_t *obj = heap_alloc(sizeof(f_fade_out_t));
                    f_fade_out_init(obj, values[0], values[1]);
                }
            }
            break;

        case FUNC_BRIGHTNESS:
            {
                if (gen_count == 1)
                {
                    f_brightness_t *obj = heap_alloc(sizeof(f_brightness_t));
                    f_brightness_init(obj, gens[0]);
                }
            }
            break;

        case FUNC_CONSTANT_COLOR:
            {
                if (color_count == 1)
                {
                    s_constant_color_t *obj = heap_alloc(sizeof(s_constant_color_t));
                    s_constant_color_init(obj, &colors[0]);
                }
            }
            break;

        case FUNC_RAND_COL_SEQ:
            {
                if (value_count == 2)
                {
                    s_random_color_seq_t *obj = heap_alloc(sizeof(s_random_color_seq_t));
                    s_random_color_seq_init(obj, values[0], values[1]);
                }
            }
            break;

        case FUNC_HSV:
            {
                if (gen_count > 1)
                {
                    s_hsv_t *obj = heap_alloc(sizeof(s_hsv_t));
                    if (gen_count > 2)
                        s_hsv_init(obj, gens[0], gens[1], gens[2]);
                    else
                    if (gen_count > 1)
                        s_hsv_init(obj, gens[0], gens[1], NULL);
                    else
                        s_hsv_init(obj, gens[0], NULL, NULL);
                }
            }
            break;

        case FUNC_RAINBOW:
            {
                if (gen_count == 1)
                {
                    s_rainbow_t *obj = heap_alloc(sizeof(s_rainbow_t));
                    s_rainbow_init(obj, gens[0]);
                }
            }
            break;
    }


    if (arg_index < len)
    {
        parse_func(code, len, &arg_index);
    }

    return NULL;
}

int main(int argc, char *argv[])
{
    FILE *fp;
    uint16_t rd, index = 0, dummy = 0;
    char code[MAX_CODE_LEN], pair[3], ch;
    
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

    parse_func(code, index, &dummy);

    return 0;
}
