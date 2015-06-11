#ifndef __DEFS_H__
#define __DEFS_H__

#include <stdint.h>

#define HEAP_SIZE              255

#define SCALE_FACTOR 1000
#define S_PIM2       6283 // PI * 2 * SCALE_FACTOR
#define S_PI         3141 // PI * SCALE_FACTOR
#define S_PID2       1570 // PI / 2 * SCALE_FACTOR

typedef struct 
{
    uint8_t c[3];
} color_t;

extern uint8_t g_error;
extern uint8_t g_node_id;
extern int32_t g_pos[3];
extern uint32_t g_random_seed;

const uint8_t ERROR_DELAY          = 50;
const uint8_t ERR_OK               = 0;
const uint8_t ERR_NO_VALID_PATTERN = 1;
const uint8_t ERR_STACK_CLASH      = 2;
const uint8_t ERR_OUT_OF_HEAP      = 3;
const uint8_t ERR_PARSE_FAILURE    = 4;

#endif
