#ifndef __GENERATOR_H__
#define __GENERATOR_H__

int32_t generator_sin(uint32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset);
int32_t generator_square(uint32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset);
int32_t generator_sawtooth(uint32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset);
int32_t generator_step(uint32_t t, int32_t period, int32_t phase, int32_t amplitude, int32_t offset);

#endif
