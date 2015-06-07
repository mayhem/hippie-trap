#include <stdio.h>
#include <math.h>
#include <math.h>
#include <stdint.h>

#define NUM_SIN_TABLE_ENTRIES 255
#define SCALE_FACTOR 1000

void generate_sin_table(void)
{
    int i;
    float v, k;

    printf("#define NUM_SIN_TABLE_ENTRIES %d\n", NUM_SIN_TABLE_ENTRIES);
    printf("int16_t sin_table[NUM_SIN_TABLE_ENTRIES] = {\n");
    for(i = 0; i < NUM_SIN_TABLE_ENTRIES; i++)
    {
        k = (float)i / NUM_SIN_TABLE_ENTRIES * 2.0 * M_PI;
        v = sin(k);
        //printf("%.3f - %.3f - %d\n", k, v, (int)(v * SCALE_FACTOR));
        printf("   %d", (int)(v * SCALE_FACTOR));
        if (i < NUM_SIN_TABLE_ENTRIES - 1)
            printf(",");
        printf("\n");
    }
    printf("};\n");
}

int main(int argc, char *argv[])
{
    generate_sin_table();
    return 0;
}
