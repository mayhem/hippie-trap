#ifndef __PARSE_H__
#define __PARSE_H__

#include "source.h"
#include "filter.h"
    
void clear_heap(void);
void *heap_alloc(uint8_t bytes);
void *parse(char *code, int16_t len);
void evaluate(s_source_t *src, uint32_t t, color_t *color);

#endif
