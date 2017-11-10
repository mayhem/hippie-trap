#ifndef __PARSE_H__
#define __PARSE_H__

#include "function.h"

extern uint32_t  g_speed;
extern pattern_t g_patterns[2];

void    setup_error_pattern(void);
uint8_t parse_pattern(uint8_t pattern_index, uint8_t *code, uint16_t len);
void    evaluate(pattern_t *pattern, uint32_t _t, uint8_t led, color_t *color);

#endif
