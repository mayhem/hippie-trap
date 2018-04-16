#ifndef COLORSPACE_H
#define COLORSPACE_H

#include "defs.h"

uint8_t hsv_to_rgb(int32_t h, int32_t s, int32_t v, color_t *color);
uint8_t rgb_to_hsv(color_t *col, int32_t *_h, int32_t *_s, int32_t *_v);

#endif
