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

int32_t function_sin(uint32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    int32_t index = (((int32_t)t * period / SCALE_FACTOR + phase) % S_PIM2) * NUM_SIN_TABLE_ENTRIES / S_PIM2;
    if (index < 0)
        index = NUM_SIN_TABLE_ENTRIES + index;
    return (int32_t)sin_table[index] * amplitude / SCALE_FACTOR + offset;
}

float float_sin(float t, float period, float phase, float amplitude, float offset)
{
    return sin(t * period + phase) * amplitude + offset;
}

int32_t function_square(uint32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    int32_t v = ((int32_t)t * SCALE_FACTOR / period) + phase;
    if (v % SCALE_FACTOR >= (SCALE_FACTOR >> 1))
        return amplitude + offset;
    else
        return offset;
}

float float_square(float t, float period, float phase, float amplitude, float offset)
{
    float v = (t / period) + phase;
    if (fmod(v,  1.0) >= .5)
        return amplitude + offset;

    return offset;
}

int32_t function_sawtooth(uint32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset)
{
    int32_t v = (((int32_t)t * period / SCALE_FACTOR) + phase) % SCALE_FACTOR;
    return v * amplitude / SCALE_FACTOR + offset;
}

float float_sawtooth(float t, float period, float phase, float amplitude, float offset)
{
    return fmod(t * period + phase, 1.0) * amplitude + offset;
}

#define TEST_ERR_THRES .1
int test(int test_id, 
         int32_t (*i_func)(uint32_t, int32_t, int32_t, int32_t, int32_t),
         float (*f_func)(float, float, float, float, float),
         float period, 
         float phase, 
         float offset, 
         float amplitude,
         float end, 
         float step)
{
    float t, f_val, i_val, d;
    int   count = 0;

    for(t = 0; t < end; t += step)
    {
        f_val = f_func(t, period, phase, amplitude, offset);
        i_val = (float)i_func(
                 (uint32_t)(t * SCALE_FACTOR), 
                 (int32_t)(period * SCALE_FACTOR), 
                 (int32_t)(phase * SCALE_FACTOR), 
                 (int32_t)(amplitude * SCALE_FACTOR), 
                 (int32_t)(offset * SCALE_FACTOR)) / (float)SCALE_FACTOR;
        d = fabs(i_val - f_val);
        if (d > TEST_ERR_THRES)
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
    printf("Sawtooth tests\n");
    test(0, function_sawtooth, float_sawtooth, 1, 0, 0, 1, 10, .1);
    test(1, function_sawtooth, float_sawtooth, 2, 0, 0, 1, 10, .1);
    test(2, function_sawtooth, float_sawtooth, .5, 0, 0, 1, 10, .1);
    test(3, function_sawtooth, float_sawtooth, 1, .5, 1, 5, 900, .1);
    test(4, function_sawtooth, float_sawtooth, 2, .5, 3, .1, 900, .1);
    test(5, function_sawtooth, float_sawtooth, .5, .5, 10, 2, 900, .1);
#if 0
    printf("Square tests\n");
    test(0, function_square, float_square, 1, 0, 0, 1, 10, .1);
    test(1, function_square, float_square, 2, 0, 0, 1, 10, .1);
    test(2, function_square, float_square, .5, 0, 0, 1, 10, .1);
    test(3, function_square, float_square, 1, .5, 1, 5, 900, .1);
    test(4, function_square, float_square, 2, .5, 3, .1, 900, .1);
    test(5, function_square, float_square, .5, .5, 10, 2, 900, .1);

    printf("Sin tests\n");
    test(0, function_sin, float_sin, 1, 0, 0, 1, 10, .1);
    test(1, function_sin, float_sin, .5, S_PI, 0, 1, 10, .1);
    test(2, function_sin, float_sin, 2, -S_PI, 0, 1, 10, .1);
    test(3, function_sin, float_sin, 1, S_PI, 0, 1, 900, .1);
    test(4, function_sin, float_sin, 1, 0, 10, 10, 10, .1);
    test(5, function_sin, float_sin, .5, S_PI, 10, .1, 10, .1);
    test(6, function_sin, float_sin, 2, -S_PID2, 50, 1, 10, .1);
    test(7, function_sin, float_sin, 1, S_PID2, 10, 2, 900, .1);
#endif
}
