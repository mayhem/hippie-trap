#include <stdio.h>
#include <math.h>
#include <math.h>
#include <stdint.h>

#define NUM_SIN_TABLE_ENTRIES 1000
#define SCALE_FACTOR 1000

void generate_sin_table(void)
{
    int i;
    float v, k;

    printf("#include <stdint.h>\n");
    printf("#include <avr/pgmspace.h>\n");
    printf("#define NUM_SIN_TABLE_ENTRIES %d\n", NUM_SIN_TABLE_ENTRIES);
    printf("const PROGMEM int16_t sin_table[NUM_SIN_TABLE_ENTRIES] = {\n    ");
    for(i = 0; i < NUM_SIN_TABLE_ENTRIES; i++)
    {
        k = (float)i / NUM_SIN_TABLE_ENTRIES * 2.0 * M_PI;
        v = sin(k);
        printf("%5d", (int)(v * SCALE_FACTOR));
        if (i < NUM_SIN_TABLE_ENTRIES - 1)
            printf(",");
        if (i && i % 20 == 0)
            printf("\n    ");
    }
    printf("\n};\n");
}

int main(int argc, char *argv[])
{
    generate_sin_table();
    return 0;
}
