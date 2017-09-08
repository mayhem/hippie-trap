#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <Arduino.h>

#include "source.h"
#include "filter.h"
#include "function.h"
#include "generator.h"
#include "parse.h"

int32_t master_brightness = 1000;

#define MAX_FUNCTIONS       12
#define DEFAULT_PERIOD      1.0
#define DEFAULT_PHASE       0.0
#define DEFAULT_AMPLITUDE   1.0
#define DEFAULT_OFFSET      0.0

#define FUNC_MAPPING_0_TO_ALL 0
#define FUNC_MAPPING_TO_ALL 0
#define FUNC_MAPPING_TO_ALL 0
#define FUNC_MAPPING_TO_ALL 0
#define FUNC_MAPPING_TO_ALL 0

#define MAPPING_MAPPING_ALL   0
#define MAPPING_INDIVIDUAL    1
#define MAPPING_LOWER_SIDE    2 
#define MAPPING_UPPER_SIDE    3
#define MAPPING_LED_0         4
#define MAPPING_LED_1         5
#define MAPPING_LED_2         6
#define MAPPING_LED_3         7
#define MAPPING_EVENS         8
#define MAPPING_ODDS          9

typedef struct s_function_t
{
    uint8_t       type;
    uint32_t      period;
    uint32_t      phase;
    uint32_t      amplitude;
    uint32_t      offset;
} s_function_t;

typedef struct s_pattern_t
{
    uint8_t      num_funcs;
    uint8_t      mapping;
    uint32_t     period;
    s_function_t functions[MAX_FUNCTIONS];
} s_pattern_t;

void parse_packet(uint8_t *code, uint16_t len, s_pattern_t *pattern)
{
    uint8_t  i, *index;
    uint8_t      mapping;
    uint32_t 

    memset(pattern, 0, sizeof(s_pattern_t));

    pattern->num_func = code[0] & 0xF;
    mapping = (code[1] << 8) | (code[0] >> 4);
    pattern->period = *(uint32_t *)&code[2];

    index = &code[6];
    for(i = 0; i < pattern->num_func; i++)
    {
        pattern->functions[i].type = *index & 0xF;
        pattern->functions[i].args = *index >> 4;
        index++;

        if (pattern->functions[i].args & 1 != 0)
            pattern->functions[i].period = *(uint32_t *)index;
        else 
            pattern->functions[i].period = DEFAULT_PERIOD;
        index += sizeof(int32_t);

        if (pattern->functions[i].args & 2 != 0)
            pattern->functions[i].phase = *(uint32_t *)index;
        else 
            pattern->functions[i].phase = DEFAULT_PHASE;
        index += sizeof(int32_t);

        if (pattern->functions[i].args & 4 != 0)
            pattern->functions[i].amplitude = *(uint32_t *)index;
        else 
            pattern->functions[i].amplitude = DEFAULT_AMPLITUDE;
        index += sizeof(int32_t);

        if (pattern->functions[i].args & 8 != 0)
            pattern->functions[i].offset = *(uint32_t *)index;
        else 
            pattern->functions[i].offset = DEFAULT_OFFSET;
        index += sizeof(int32_t);
    }
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

void set_brightness(int32_t brightness)
{
    master_brightness = brightness;
}
