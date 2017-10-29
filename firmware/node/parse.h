#ifndef __PARSE_H__
#define __PARSE_H__

#include "function.h"

extern uint32_t g_speed;

void heap_setup(uint8_t *heap);
uint8_t parse_packet(uint8_t *code, uint16_t len, pattern_t *pattern);
void  evaluate(pattern_t *pattern, uint32_t _t, uint8_t led, color_t *color);

#endif
