#include <Arduino.h>
#include <stdlib.h>
#include "generator.h"
#include "function.h"

void fu_local_random_init(fu_local_random_t *self, int32_t lower, int32_t upper)
{
    self->method = fu_local_random_get;
    self->next = NULL;
    self->upper = upper;
    self->lower = lower;
}

void fu_local_random_get(void *_self, uint32_t t, int32_t *dest)
{
    fu_local_random_t *self = (fu_local_random_t *)_self;
    
    *dest = random(self->lower, self->upper);
}
