#include <stdio.h>
#include <math.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>

#include "sin_table.h"
#include "generator.h"
#include "defs.h"

float float_sin(float t, float period, float phase, float amplitude, float offset)
{
    return sin(t * period + phase) * amplitude + offset;
}

float float_square(float t, float period, float phase, float amplitude, float offset)
{
    float v = (t / period) + phase;
    if (fmod(v,  1.0) >= .5)
        return amplitude + offset;

    return offset;
}

float float_sawtooth(float t, float period, float phase, float amplitude, float offset)
{
    return fmod(t * period + phase, 1.0) * amplitude + offset;
}

float float_step(float t, float period, float phase, float amplitude, float offset)
{
    float v = (t / period) + phase;
    if (v >= 0.0)
        return amplitude + offset;

    return offset;
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
    printf("Step tests\n");
    test(0, generator_step, float_step, 1, 0, 0, 1, 10, .1);
    test(1, generator_step, float_step, 2, 0, 0, 1, 10, .1);
    test(2, generator_step, float_step, 1, -2, 1, .5, 10, .1);
    test(3, generator_step, float_step, 1, .5, 1, 5, 900, .1);
    test(4, generator_step, float_step, 2, .5, 3, .1, 900, .1);
    test(5, generator_step, float_step, .5, .5, 10, 2, 900, .1);
#if 0
    printf("Sawtooth tests\n");
    test(0, generator_sawtooth, float_sawtooth, 1, 0, 0, 1, 10, .1);
    test(1, generator_sawtooth, float_sawtooth, 2, 0, 0, 1, 10, .1);
    test(2, generator_sawtooth, float_sawtooth, .5, 0, 0, 1, 10, .1);
    test(3, generator_sawtooth, float_sawtooth, 1, .5, 1, 5, 900, .1);
    test(4, generator_sawtooth, float_sawtooth, 2, .5, 3, .1, 900, .1);
    test(5, generator_sawtooth, float_sawtooth, .5, .5, 10, 2, 900, .1);
    printf("Square tests\n");
    test(0, generator_square, float_square, 1, 0, 0, 1, 10, .1);
    test(1, generator_square, float_square, 2, 0, 0, 1, 10, .1);
    test(2, generator_square, float_square, .5, 0, 0, 1, 10, .1);
    test(3, generator_square, float_square, 1, .5, 1, 5, 900, .1);
    test(4, generator_square, float_square, 2, .5, 3, .1, 900, .1);
    test(5, generator_square, float_square, .5, .5, 10, 2, 900, .1);

    printf("Sin tests\n");
    test(0, generator_sin, float_sin, 1, 0, 0, 1, 10, .1);
    test(1, generator_sin, float_sin, .5, S_PI, 0, 1, 10, .1);
    test(2, generator_sin, float_sin, 2, -S_PI, 0, 1, 10, .1);
    test(3, generator_sin, float_sin, 1, S_PI, 0, 1, 900, .1);
    test(4, generator_sin, float_sin, 1, 0, 10, 10, 10, .1);
    test(5, generator_sin, float_sin, .5, S_PI, 10, .1, 10, .1);
    test(6, generator_sin, float_sin, 2, -S_PID2, 50, 1, 10, .1);
    test(7, generator_sin, float_sin, 1, S_PID2, 10, 2, 900, .1);
#endif
}
