#include <Arduino.h>
#include <stdlib.h>
#include "generator.h"
#include "function.h"

int32_t fu_local_random(int32_t lower, int32_t upper)
{
    return random(lower, upper);
}
