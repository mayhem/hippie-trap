#ifndef __DEFS_H__
#define __DEFS_H__

#include <stdint.h>

#define HEAP_SIZE           256
#define MAX_FUNCTIONS       256
#define MAX_ARGS            8
#define NUM_PIXELS          4

#define SCALE_FACTOR 1000
#define S_PIM2       6283 // PI * 2 * SCALE_FACTOR
#define S_PI         3141 // PI * SCALE_FACTOR
#define S_PID2       1570 // PI / 2 * SCALE_FACTOR

typedef struct 
{
    uint8_t r,g,b;
} color_t;

extern uint8_t g_node_id;
extern int16_t g_pos[3];
extern int32_t g_angle;
extern uint32_t g_random_seed;

void print_col(color_t *col);
void set_error(uint8_t err);

const uint8_t ERROR_DELAY          = 255;
const uint8_t ERR_OK               = 0;
const uint8_t ERR_NO_VALID_PATTERN = 1;
const uint8_t ERR_STACK_CLASH      = 2;
const uint8_t ERR_OUT_OF_HEAP      = 3;
const uint8_t ERR_PARSE_FAILURE    = 4;

void  dprintf(const char *fmt, ...);

#endif
