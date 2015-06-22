#include <Arduino.h>
#include <stdlib.h>
#include "generator.h"
#include "function.h"

void f_local_random_init(f_local_random_t *self, int32_t lower, int32_t upper)
{
    self->method = f_local_random_get;
    self->next = NULL;
    self->upper = upper;
    self->lower = lower;
}

void f_local_random_get(void *_self, uint32_t t, int32_t *dest)
{
    f_local_random_t *self = (f_local_random_t *)_self;
    
    *dest = random(self->lower, self->upper);
}
