#include <stdint.h>
#include <avr/pgmspace.h>

#define NUM_SIN_TABLE_ENTRIES 255
const PROGMEM int16_t sin_table[NUM_SIN_TABLE_ENTRIES] = {
   0,
   24,
   49,
   73,
   98,
   122,
   147,
   171,
   195,
   219,
   243,
   267,
   291,
   314,
   338,
   361,
   384,
   406,
   429,
   451,
   473,
   494,
   515,
   536,
   557,
   577,
   597,
   617,
   636,
   655,
   673,
   691,
   709,
   726,
   743,
   759,
   775,
   790,
   805,
   819,
   833,
   846,
   859,
   872,
   883,
   895,
   905,
   916,
   925,
   934,
   943,
   951,
   958,
   965,
   971,
   976,
   981,
   986,
   989,
   993,
   995,
   997,
   999,
   999,
   999,
   999,
   998,
   996,
   994,
   991,
   988,
   984,
   979,
   974,
   968,
   961,
   954,
   947,
   938,
   930,
   920,
   911,
   900,
   889,
   878,
   866,
   853,
   840,
   826,
   812,
   798,
   782,
   767,
   751,
   734,
   717,
   700,
   682,
   664,
   645,
   626,
   607,
   587,
   567,
   547,
   526,
   505,
   483,
   462,
   440,
   417,
   395,
   372,
   349,
   326,
   303,
   279,
   255,
   231,
   207,
   183,
   159,
   135,
   110,
   86,
   61,
   36,
   12,
   -12,
   -36,
   -61,
   -86,
   -110,
   -135,
   -159,
   -183,
   -207,
   -231,
   -255,
   -279,
   -303,
   -326,
   -349,
   -372,
   -395,
   -417,
   -440,
   -462,
   -483,
   -505,
   -526,
   -547,
   -567,
   -587,
   -607,
   -626,
   -645,
   -664,
   -682,
   -700,
   -717,
   -734,
   -751,
   -767,
   -782,
   -798,
   -812,
   -826,
   -840,
   -853,
   -866,
   -878,
   -889,
   -900,
   -911,
   -920,
   -930,
   -938,
   -947,
   -954,
   -961,
   -968,
   -974,
   -979,
   -984,
   -988,
   -991,
   -994,
   -996,
   -998,
   -999,
   -999,
   -999,
   -999,
   -997,
   -995,
   -993,
   -989,
   -986,
   -981,
   -976,
   -971,
   -965,
   -958,
   -951,
   -943,
   -934,
   -925,
   -916,
   -905,
   -895,
   -883,
   -872,
   -859,
   -846,
   -833,
   -819,
   -805,
   -790,
   -775,
   -759,
   -743,
   -726,
   -709,
   -691,
   -673,
   -655,
   -636,
   -617,
   -597,
   -577,
   -557,
   -536,
   -515,
   -494,
   -473,
   -451,
   -429,
   -406,
   -384,
   -361,
   -338,
   -314,
   -291,
   -267,
   -243,
   -219,
   -195,
   -171,
   -147,
   -122,
   -98,
   -73,
   -49,
   -24
};