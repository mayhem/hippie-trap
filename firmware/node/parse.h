#ifndef __PARSE_H__
#define __PARSE_H__

#include "source.h"
#include "filter.h"
    
void heap_setup(uint8_t *heap);
void *heap_alloc(uint8_t *heap, uint8_t bytes);
void *parse(uint8_t *code, uint16_t len, uint8_t *heap);
void evaluate(s_source_t *src, uint32_t t, color_t *color);

#endif
