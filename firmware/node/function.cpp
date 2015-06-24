#include <Arduino.h>
#include <stdlib.h>
#include "generator.h"
#include "function.h"

const uint8_t MAX_LOCAL_RANDOM_VALUES = 6;
int32_t g_random_values[MAX_LOCAL_RANDOM_VALUES];
uint8_t g_num_random_values = 0;

void clear_local_random_values(void)
{
    g_num_random_values = 0;
}

int32_t fu_local_random(int32_t lower, int32_t upper)
{
    int32_t r = random(lower, upper);
    
    if (g_num_random_values < MAX_LOCAL_RANDOM_VALUES)
        g_random_values[g_num_random_values++] = r;
        
    return r;
}

int32_t fu_repeat_local_random(int32_t index)
{
    if (g_num_random_values > index && g_num_random_values < MAX_LOCAL_RANDOM_VALUES)
        return g_random_values[index];

    return 0;
}
