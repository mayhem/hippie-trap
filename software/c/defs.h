#ifndef __DEFS_H__
#define __DEFS_H__

#define SCALE_FACTOR 1000
#define S_PIM2       6283 // PI * 2 * SCALE_FACTOR
#define S_PI         3141 // PI * SCALE_FACTOR
#define S_PID2       1570 // PI / 2 * SCALE_FACTOR

struct color_t
{
    uint8_t c[3];
};

#endif
