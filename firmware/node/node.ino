#include <util/crc16.h>
#include <EEPROM.h>
#include <Adafruit_NeoPixel.h>
#include "parse.h"

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

// where in EEPROM our node id is stored
const int id_address = 0;

// ----- globals ------------

uint8_t    g_error = ERR_OK;

// time keeping
uint32_t   g_target = 0, g_pattern_start = 0;
uint8_t    g_delay = 10;

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

// ---- prototypes -----
void next_pattern(void);

void show_color(color_t *col)
{
    uint8_t j;
    
    for(j = 0; j < NUM_PIXELS; j++)
        if (col)
            g_pixels.setPixelColor(j, col->c[0], col->c[1], col->c[2]);
        else
            g_pixels.setPixelColor(j, 0, 0, 0); 
           
    g_pixels.show();
}

void startup_animation(void)
{
    uint8_t i, j;
 
    uint8_t col1[3] = { 128, 40, 0 };
    uint8_t col2[3] = { 128, 0, 128 };

    for(i = 0; i < 10; i++)
    {       
        for(j = 0; j < NUM_PIXELS; j++)
        {
            if (i % 2 == 0)
            {
                if (j % 2 == 1)
                    g_pixels.setPixelColor(j, col1[0], col1[1], col1[2]);
                else
                    g_pixels.setPixelColor(j, 0, 0, 0);    
            }
            else
            {
                if (j % 2 == 0)
                    g_pixels.setPixelColor(j, col2[0], col2[1], col2[2]);
                else
                    g_pixels.setPixelColor(j, 0, 0, 0);  
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
    if (target != BROADCAST && target != g_node_id)
         return;
    
    type = packet[1];
    data = &packet[2];
    switch(type)
    {
        case PACKET_SINGLE_COLOR:
            for(int j=0; j < NUM_PIXELS; j++)
                g_pixels.setPixelColor(j, g_pixels.Color(data[0], data[1], data[2]));
            break;
            
        case PACKET_COLOR_ARRAY:
            for(int j=0; j < NUM_PIXELS; j++, data += 3)
                g_pixels.setPixelColor(j, g_pixels.Color(data[0], data[1], data[2]));      
            break;  
            
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

                Serial.println("Parse ok.");
                // we parsed a valid pattern, increase the index
                g_load_pattern= (g_load_pattern + 1) % 2;

                break;  
            }

        case PACKET_NEXT:
            next(data[0]);
            break;

        case PACKET_CLEAR_NEXT:
            clear_next_pattern();
            break;

        case PACKET_OFF:
            {
                color_t col;

                col.c[0] = col.c[1] = col.c[2] = 0;
                g_cur_pattern = g_next_pattern = NULL;
                g_error = ERR_OK;
                show_color(&col);
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
    }
}

void next(uint16_t transition_steps)
{
    if (!g_next_pattern)
    {
        g_error = ERR_NO_VALID_PATTERN;
        return;
    }

    if (transition_steps)
    {
        g_transition_steps = transition_steps;

        // start the transition and get last color
        evaluate(g_cur_pattern, millis() - g_pattern_start, &g_end_color);

        // get the first color of the new pattern
        evaluate(g_next_pattern, 0, &g_begin_color);

        g_transition_end = millis() + transition_steps;
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
    
    g_pattern_start = millis();
    g_target = g_pattern_start;
  
    evaluate(g_cur_pattern, g_pattern_start, &color);
    for(i = 0; i < NUM_PIXELS; i++)
        g_pixels.setPixelColor(i, color.c[0], color.c[1], color.c[2]); 

    g_error = ERR_OK;
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
    if (g_transition_end >= millis())
    {
        g_transition_end = 0;
        g_transition_steps = 0;
        next_pattern();
        return;
    }

    // check for a transition
    if (g_transition_end)
    {
        int32_t steps;

        steps = (g_end_color.c[0] - g_begin_color.c[0]) * SCALE_FACTOR / g_transition_steps;
        color.c[0] = g_begin_color.c[0] + (steps * (g_transition_end - millis()) / SCALE_FACTOR); 

        steps = (g_end_color.c[1] - g_begin_color.c[1]) * SCALE_FACTOR / g_transition_steps;
        color.c[1] = g_begin_color.c[1] + (steps * (g_transition_end - millis()) / SCALE_FACTOR); 

        steps = (g_end_color.c[2] - g_begin_color.c[0]) * SCALE_FACTOR / g_transition_steps;
        color.c[2] = g_begin_color.c[2] + (steps * (g_transition_end - millis()) / SCALE_FACTOR); 

        for(i = 0; i < NUM_PIXELS; i++)
            g_pixels.setPixelColor(i, color.c[0], color.c[1], color.c[2]); 

        return;
    }

    if (!g_cur_pattern)
        return;
       
    if (g_target && millis() >= g_target)
    {
        g_target += g_delay;
        g_pixels.show();

        evaluate(g_cur_pattern, g_target - g_pattern_start, &color);
        for(i = 0; i < NUM_PIXELS; i++)
            g_pixels.setPixelColor(i, color.c[0], color.c[1], color.c[2]); 
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

    t = millis() % (ERROR_DELAY * 2);
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
                 col.c[0] = 128;
                 break;
        }
        show_color(&col);
    }
    else
        show_color(NULL);
}

void setup()
{ 
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
