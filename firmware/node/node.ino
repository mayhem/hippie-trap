#include <util/crc16.h>
#include <EEPROM.h>
#include <Adafruit_NeoPixel.h>
#include <avr/pgmspace.h>
#include "parse.h"

const uint8_t NUM_NODES = 101;
const uint8_t NUM_PIXELS = 4;
const uint8_t OUT_PIN = 2;

const uint16_t MAX_PACKET_LEN     = 200;
const uint8_t BROADCAST = 0;
const uint8_t PACKET_SINGLE_COLOR = 0;
const uint8_t PACKET_COLOR_ARRAY  = 1;
const uint8_t PACKET_PATTERN      = 2;
const uint8_t PACKET_ENTROPY      = 3;
const uint8_t PACKET_NEXT         = 4;
const uint8_t PACKET_OFF          = 5;
const uint8_t PACKET_CLEAR_NEXT   = 6;
const uint8_t PACKET_POSITION     = 7;
const uint8_t PACKET_DELAY        = 8;
const uint8_t PACKET_ADDR         = 9;
const uint8_t PACKET_SPEED        = 10;
const uint8_t PACKET_CLASSES      = 11;

// where in EEPROM our node id is stored
const int id_address = 0;

// ----- globals ------------

uint8_t    g_error = ERR_OK;

// time keeping
uint32_t   g_target = 0, g_pattern_start = 0;
uint8_t    g_delay = 10;
uint32_t   g_speed = SCALE_FACTOR;

// random seed
uint32_t    g_random_seed = 0;

// The current packet
uint8_t     g_packet[MAX_PACKET_LEN];
s_source_t *g_cur_pattern = NULL;
s_source_t *g_next_pattern = NULL;

// this is where the parsed patterns live
uint8_t g_pattern_space[HEAP_SIZE * 2];
// this keeps track of where the next pattern should be written to 
int8_t g_load_pattern = 0;

// The LED control object
Adafruit_NeoPixel g_pixels = Adafruit_NeoPixel(NUM_PIXELS, OUT_PIN, NEO_GRB + NEO_KHZ800);

// our node id
uint8_t g_node_id = 0;

// color/step information for transitions
uint32_t g_transition_end = 0;
uint16_t g_transition_steps = 0;
color_t  g_begin_color, g_end_color;

// location in space
int32_t g_pos[3];
int8_t  g_ring = -1;
int8_t  g_arm = -1;

// broadcast classes
const uint8_t NUM_CLASSES = 10;
const uint8_t NO_CLASS = 255;
uint8_t g_classes[NUM_CLASSES];

// Gamma correction table in progmem
const uint8_t PROGMEM gamma[] = {
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255 
};

// ---- prototypes -----
void next_pattern(void);

#if F_CPU == 16000000UL
#define    TIMER1_INIT         0xF82F
#else
#define    TIMER1_INIT         0xFC17
#endif
#define    TIMER1_FLAGS        _BV(CS11); // 8Mhz / 8 = 1us per tick.

volatile uint32_t g_time = 0;
uint16_t g_timer_init = TIMER1_INIT;

ISR (TIMER1_OVF_vect)
{
    g_time++;
    TCNT1 = g_timer_init;
}

uint32_t cmillis(void)
{
    uint32_t temp;

    noInterrupts();
    temp = g_time;
    interrupts();

    return temp;
}

void show_color(color_t *col)
{
    uint8_t j;
   
    for(j = 0; j < NUM_PIXELS; j++)
        if (col)
            g_pixels.setPixelColor(j, 
                pgm_read_byte(&gamma[col->c[0]]),
                pgm_read_byte(&gamma[col->c[1]]),
                pgm_read_byte(&gamma[col->c[2]]));
        else
            g_pixels.setPixelColor(j, 0, 0, 0); 
           
    g_pixels.show();
}

void set_pixel_color(uint8_t index, color_t *col)
{
    if (col)
    {
        g_pixels.setPixelColor(index,
            pgm_read_byte(&gamma[col->c[0]]),
            pgm_read_byte(&gamma[col->c[1]]),
            pgm_read_byte(&gamma[col->c[2]]));
    }
    else
        g_pixels.setPixelColor(index, 0, 0, 0);
}

void startup_animation(void)
{
    uint8_t i, j;
    color_t col1, col2;

    col1.c[0] = 255;
    col1.c[1] = 140;
    col1.c[2] = 0;
    col2.c[0] = 255;
    col2.c[1] = 0;
    col2.c[2] = 255;

    for(i = 0; i < 10; i++)
    {       
        for(j = 0; j < NUM_PIXELS; j++)
        {
            if (i % 2 == 0)
            {
                if (j % 2 == 1)
                    set_pixel_color(j, &col1);
                else
                    set_pixel_color(j, NULL);
            }
            else
            {
                if (j % 2 == 0)
                    set_pixel_color(j, &col2);
                else
                    set_pixel_color(j, NULL);  
            }
        }   
        g_pixels.show();
        delay(100);
    }
    show_color(NULL);
}

void handle_packet(uint16_t len, uint8_t *packet)
{
    uint8_t    j, type, target;
    uint8_t   *data;

    target = packet[0];
    if (target > NUM_NODES + 1)
    {
        uint8_t cls = target - (NUM_NODES + 1), i;

        for(i = 0; i < NUM_CLASSES; i++)
            if (g_classes[i] == cls)
            {
                target = g_node_id;
                break;
            }
    }

    if (target != BROADCAST && target != g_node_id)
         return;
    
    type = packet[1];
    data = &packet[2];
    switch(type)
    {
        case PACKET_SINGLE_COLOR:
            {
                color_t col;
                col.c[0] = data[0];
                col.c[1] = data[1];
                col.c[2] = data[2];

                //print_col(&col);
                for(int j=0; j < NUM_PIXELS; j++)
                    show_color(&col);

                break;
            } 
        case PACKET_COLOR_ARRAY:
            {
                color_t col;

                for(int j=0; j < NUM_PIXELS; j++, data += 3)
                {
                    col.c[0] = data[0];
                    col.c[1] = data[1];
                    col.c[2] = data[2];
                    set_pixel_color(j, &col);
                }
                g_pixels.show();
                break;  
            }
            
        case PACKET_PATTERN:
            {
                uint8_t *heap, err;


                // If I already have a pattern and a new pattern is sent, ignore it. It is a 
                // redundant transmission in case we have communication problems.
                if (g_next_pattern)
                    return;

                heap = &g_pattern_space[g_load_pattern * HEAP_SIZE];
                g_next_pattern = (s_source_t *)parse(data, len - 2, heap);
                if (!g_next_pattern)
                {
                    Serial.println("Parse failed.");
                    g_next_pattern = NULL;
                    return;
                }

                // we parsed a valid pattern, increase the index
                g_load_pattern= (g_load_pattern + 1) % 2;

                break;  
            }

        case PACKET_NEXT:
            next(*(uint16_t *)data);
            break;

        case PACKET_CLEAR_NEXT:
            clear_next_pattern();
            break;

        case PACKET_OFF:
            {
                g_cur_pattern = g_next_pattern = NULL;
                g_error = ERR_OK;
                g_load_pattern = 0;
                g_transition_end = 0;
                g_target = 0;
                show_color(NULL);
            }
            break;
            
        case PACKET_ENTROPY:
            {
                color_t col;

                g_random_seed = data[0];
                randomSeed(g_random_seed);

                col.c[0] = col.c[2] = 0;
                col.c[1] = 180;
                show_color(&col);
            }
            break;  
            
        case PACKET_POSITION:
            {
                color_t col;
                g_pos[0] = data[0];
                g_pos[1] = data[1];
                g_pos[2] = data[2];

                col.c[0] = col.c[1] = 0;
                col.c[2] = 180;
                show_color(&col);
            }
            break;  

        case PACKET_DELAY:
            g_delay = data[0];
            break;  

        case PACKET_SPEED:
            g_speed = data[0];
            break;  

        case PACKET_CLASSES:
            {
                uint8_t i;

                for(i = 0; i < NUM_CLASSES; i++)
                    g_classes[i] = NO_CLASS;

                for(i = 0; i < len - 2; i++)
                {
                    Serial.println("set class " + String(data[i]));
                    g_classes[i] = data[i];
                }

                break;
            }
    }
}

void print_col(color_t *c)
{
    Serial.print(c->c[0], DEC);
    Serial.print(", ");
    Serial.print(c->c[1], DEC);
    Serial.print(", ");
    Serial.println(c->c[2], DEC);
}

void next(uint16_t transition_steps)
{
    
    if (!g_next_pattern)
    {
        g_error = ERR_NO_VALID_PATTERN;
        return;
    }

    if (transition_steps && g_cur_pattern)
    {
        g_transition_steps = transition_steps;

        // start the transition and get last color
        evaluate(g_cur_pattern, cmillis() - g_pattern_start, &g_begin_color);

        // get the first color of the new pattern
        evaluate(g_next_pattern, 0, &g_end_color);

        g_transition_end = cmillis() + (uint32_t)transition_steps;
        return;
    }
    next_pattern();
}

void next_pattern(void)
{
    uint8_t  i;
    color_t     color;
        
    g_cur_pattern = g_next_pattern;
    g_next_pattern = NULL;
    
    g_pattern_start = cmillis();
    g_target = g_pattern_start;
    g_error = ERR_OK;
    update_pattern();
}    

void update_pattern(void)
{
    uint8_t  i;
    color_t  color;

    if (g_error)
    {
        error_pattern();
        return;
    }

    // check to see if the transtion is finished
    if (g_transition_end && cmillis() >= g_transition_end)
    {
        g_transition_end = 0;
        g_transition_steps = 0;
        next_pattern();
        return;
    }

    // check for a transition
    if (g_transition_end)
    {
        if (cmillis() >= g_target)
        {
            int32_t steps;
            int32_t p = g_transition_steps - (g_transition_end - cmillis());
            
            g_target += g_delay;
            g_pixels.show();

            steps = (int32_t)(g_end_color.c[0] - g_begin_color.c[0]) * SCALE_FACTOR / g_transition_steps;
            color.c[0] = g_begin_color.c[0] + (steps * p / SCALE_FACTOR); 

            steps = (int32_t)(g_end_color.c[1] - g_begin_color.c[1]) * SCALE_FACTOR / g_transition_steps;
            color.c[1] = g_begin_color.c[1] + (steps * p / SCALE_FACTOR); 

            steps = (int32_t)(g_end_color.c[2] - g_begin_color.c[2]) * SCALE_FACTOR / g_transition_steps;
            color.c[2] = g_begin_color.c[2] + (steps * p / SCALE_FACTOR); 

            for(i = 0; i < NUM_PIXELS; i++)
                set_pixel_color(i, &color); 
        }
        return;
    }

    if (!g_cur_pattern)
        return;
       
    if (g_target && cmillis() >= g_target)
    {
        g_target += g_delay;
        g_pixels.show();

        evaluate(g_cur_pattern, g_target - g_pattern_start, &color);
        for(i = 0; i < NUM_PIXELS; i++)
            set_pixel_color(i, &color);
        //print_col(&color); 
    }
}

void clear_next_pattern(void)
{
    g_next_pattern = NULL;
    g_load_pattern= (g_load_pattern + 1) % 2;
}

void error_pattern(void)
{
    uint8_t  t;
    uint8_t  i;
    color_t  col;

    t = cmillis() % (ERROR_DELAY * 2);
    if (t > ERROR_DELAY)
    {
        switch(g_error)
        {
            case ERR_NO_VALID_PATTERN: // orange
                 col.c[0] = 128;
                 col.c[1] = 40;
                 col.c[0] = 0;
                 break;

            case ERR_STACK_CLASH:  // red
                 col.c[0] = 255;
                 col.c[1] = col.c[2] = 0;
                 break;

            case ERR_OUT_OF_HEAP:  // green
                 col.c[1] = 255;
                 col.c[0] = col.c[2] = 0;
                 break;

            case ERR_PARSE_FAILURE:  // blue
                 col.c[2] = 255;
                 col.c[0] = col.c[1] = 0;
                 break;

            default:    
                 col.c[0] = 128;
                 col.c[1] = 0;
                 col.c[2] = 128;
                 break;
        }
        show_color(&col);
    }
    else
        show_color(NULL);
}

void setup()
{ 

    TCNT1 = TIMER1_INIT;
    TIMSK1 |= (1<<TOIE1);

    g_pixels.begin();
    startup_animation();
    
    Serial.begin(38400);
    Serial.println("led-board hello!");
    
    g_node_id = EEPROM.read(id_address);
}

void loop()
{
    uint8_t            i, ch, data[3];
    static uint8_t     found_header = 0;
    static uint16_t    crc = 0, len = 0, recd = 0;
    
    update_pattern();
    
    if (Serial.available() > 0) 
    {
        ch = Serial.read();
        if (!found_header)
        {
            if (ch == 0xFF)
            {
                found_header = 1;
            }
        }
        else
        {
            if (!len)
            {
                // We just found the header, now a realistic packet size must follow
                if (ch > 0 && ch <= MAX_PACKET_LEN)
                {
                    len = ch;
                    recd = 0;
                }
                else
                    // Nope, that was no header, better keep looking.
                    found_header = 0;
            }
            else
            {
                g_packet[recd++] = ch;
                
                if (recd <= len - 2)
                    crc = _crc16_update(crc, ch);

                if (recd == len || recd == MAX_PACKET_LEN)
                {
                    uint16_t *pcrc;
                            
                            
                    // if we received the right length, check the crc. If that matches, we have a packet!
                    if (recd == len)
                    {            
                        pcrc = (uint16_t *)(g_packet + len - 2);
                        if (crc == *pcrc)
                            handle_packet(len - 2, g_packet);
                    }

                    len = 0;
                    crc = 0;
                    found_header = 0;
                    recd = 0;
                }
            }
        }
    }

}
