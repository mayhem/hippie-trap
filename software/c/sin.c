#include <stdio.h>
#include <math.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>

#include "sin_table.h"

#define SCALE_FACTOR 1000
#define S_PIM2       6283 // PI * 2 * SCALE_FACTOR
#define S_PI         3141 // PI * SCALE_FACTOR
#define S_PID2       1570 // PI / 2 * SCALE_FACTOR

int32_t function_sin(int32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    int32_t index = ((t * period / SCALE_FACTOR + phase) % S_PIM2) * NUM_SIN_TABLE_ENTRIES / S_PIM2;
    if (index < 0)
        index = NUM_SIN_TABLE_ENTRIES + index;
    return (int32_t)sin_table[index] * amplitude / SCALE_FACTOR + offset;
}

#define SIN_TEST_ERR_THRES .059
int sin_test(int test_id, float period, float phase, float offset, float amplitude,float start, float end, float step)
{
    float t, f_val, i_val, d;
    int   count = 0;

    for(t = start; t < end; t += step)
    {
        f_val = sin(t * period + phase) * amplitude + offset;
        i_val = (float)function_sin(
                 (int32_t)(t * SCALE_FACTOR), 
                 (int32_t)(period * SCALE_FACTOR), 
                 (int32_t)(phase * SCALE_FACTOR), 
                 (int32_t)(amplitude * SCALE_FACTOR), 
                 (int32_t)(offset * SCALE_FACTOR)) / (float)SCALE_FACTOR;
        d = fabs(i_val - f_val);
        if (d > SIN_TEST_ERR_THRES)
        {
            printf("t: %.3f f: %.4f i: %.4f d: %.2f\n", t, f_val, i_val, d);
            count++;
        }
    }
    if (count)
    {
        printf("test %d: FAIL %d errors on sin_test\n", test_id, count);
        return 0;
    }
    printf("test %d: PASS\n", test_id);
    return 1;
}

int main(int argc, char *argv[])
{
    sin_test(0, 1, 0, 0, 1, -10, 10, .1);
    sin_test(1, 1, 0, 0, 1, -10, 10, .1);
    sin_test(2, 1, 1, 0, 1, -10, 10, .1);
    sin_test(3, 1, 0, 0, 1, -1000, 10000, .1);
}
