#include <stdio.h>
#include <math.h>
#include <math.h>
#include <stdint.h>

#include "sin_table.h"

#define SCALE_FACTOR 1000
#define S_PIM2      6283
#define S_PI        3141
#define S_PID2      1570

int32_t function_sin(int32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    int32_t k, v = 0;

//    printf("period: %d\n", period);
//    printf("phase: %d\n", phase);
//    printf("amplitude: %d\n", amplitude);
//    printf("offset: %d\n", offset);
    
    k = sin_table[((t * period / SCALE_FACTOR + phase) % S_PIM2) * NUM_SIN_TABLE_ENTRIES / S_PIM2];
    //k = (t * period / SCALE_FACTOR + phase) * amplitude + offset;
    printf("%d: %d\n", t, k);

    return v;
}

int main(int argc, char *argv[])
{
    int32_t t, step = 100, period;
    
    period = 2000;
    for(t = 0; t < period; t += step)
        function_sin(t, S_PIM2 * SCALE_FACTOR / period, S_PI, 1000, 0);
//    printf("%d: %d\n", 0, function_sin(0, S_PIM2 * SCALE_FACTOR / period, -S_PID2, 500, 500));
//    printf("%d: %d\n", 1000, function_sin(1000, S_PIM2 * SCALE_FACTOR / period, -S_PID2, 500, 500));

    return 0;
}
