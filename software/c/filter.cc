#ifndef __FILTER_H__
#define __FILTER_H__

#include <stdlib.h>
#include "generator.h"
#include "defs.h"

class Filter
{
    public:

        virtual void calculate(uint32_t t, color_t &in_col, color_t &out_col) = 0;
};

class FilterFadeIn : public Filter
{
    public:

        FilterFadeIn(int32_t _duration, int32_t _offset)
        {
            duration = _duration;
            offset = _offset;
        };
        void calculate(uint32_t t, color_t &in_col, color_t &out_col)
        {
            if (t < offset)
            {
                out_col.c[0] = out_col.c[1] = out_col.c[2] = 0;
                return;
            }
            if (t < offset + duration)
            {
                int32_t percent = (t - offset) * SCALE_FACTOR / duration;
                out_col.c[0] = in_col.c[0] * percent / SCALE_FACTOR;
                out_col.c[1] = in_col.c[1] * percent / SCALE_FACTOR;
                out_col.c[2] = in_col.c[2] * percent / SCALE_FACTOR;
            }
        }

    protected:

        int32_t duration;
        int32_t offset;
};

class FilterFadeOut : public Filter
{
    public:

        FilterFadeOut(int32_t _duration, int32_t _offset)
        {
            duration = _duration;
            offset = _offset;
        };
        void calculate(uint32_t t, color_t &in_col, color_t &out_col)
        {
            if (t > offset + duration)
            {
                out_col.c[0] = out_col.c[1] = out_col.c[2] = 0;
                return;
            }
            if (t > offset)
            {
                int32_t percent = SCALE_FACTOR - ((t - offset) * SCALE_FACTOR / duration);
                out_col.c[0] = in_col.c[0] * percent / SCALE_FACTOR;
                out_col.c[1] = in_col.c[1] * percent / SCALE_FACTOR;
                out_col.c[2] = in_col.c[2] * percent / SCALE_FACTOR;
            }
        }

    protected:

        int32_t duration;
        int32_t offset;
};

class FilterBrightness : public Filter
{
    public:

        FilterBrightness(Generator *_gen)
        {
            gen = _gen;
        };
        void calculate(uint32_t t, color_t &in_col, color_t &out_col)
        {
            int32_t percent = gen->calculate(t);
            out_col.c[0] = in_col.c[0] * percent / SCALE_FACTOR;
            out_col.c[1] = in_col.c[1] * percent / SCALE_FACTOR;
            out_col.c[2] = in_col.c[2] * percent / SCALE_FACTOR;
        }

    protected:

        Generator *gen;
};
#endif
