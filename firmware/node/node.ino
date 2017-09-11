#include <TimerOne.h>

#include <util/crc16.h>
#include <EEPROM.h>
#include <Adafruit_NeoPixel.h>
#include <avr/pgmspace.h>
#include <stdarg.h>
#include "parse.h"

const uint8_t NODE_ID_UNKNOWN = 255;
const uint8_t MAX_NODES = 120;
const uint8_t OUT_PIN = 2;
const uint8_t US_PER_TICK = 25;

const uint16_t MAX_PACKET_LEN     = 230;
const uint8_t BROADCAST = 0;
const uint8_t PACKET_SET_ID       = 0;
const uint8_t PACKET_CLEAR_ID     = 1; 
const uint8_t PACKET_SINGLE_COLOR = 2; 
const uint8_t PACKET_COLOR_ARRAY  = 3; 
const uint8_t PACKET_PATTERN      = 4; 
const uint8_t PACKET_ENTROPY      = 5; 
const uint8_t PACKET_START        = 6; 
const uint8_t PACKET_OFF          = 7; 
const uint8_t PACKET_CLEAR_NEXT   = 8; 
const uint8_t PACKET_POSITION     = 9; 
const uint8_t PACKET_DELAY        = 10;
const uint8_t PACKET_ADDR         = 11;
const uint8_t PACKET_SPEED        = 12;
const uint8_t PACKET_CLASSES      = 13;
const uint8_t PACKET_CALIBRATE    = 14;
const uint8_t PACKET_BRIGHTNESS   = 15;
const uint8_t PACKET_ANGLE        = 16;

// where in EEPROM our node id is stored
const int id_address = 0;
const int calibration_address = 10;

// ----- globals ------------
uint8_t    g_error = ERR_OK;

// time keeping
uint32_t   g_target = 0;
uint8_t    g_delay = 10;
uint32_t   g_speed = SCALE_FACTOR;
uint32_t   g_ticks_per_sec = (int32_t)1000000 / US_PER_TICK;
uint32_t   g_ticks_per_frame; // setup later

// random seed
uint32_t    g_random_seed = 0;

// pattern, packet, heap
uint8_t     g_pattern_active = 0;
uint8_t     g_have_valid_pattern = 0;
pattern_t   g_pattern;
uint8_t     g_packet[MAX_PACKET_LEN];
uint8_t     g_heap[HEAP_SIZE];

// The LED control object
Adafruit_NeoPixel g_pixels = Adafruit_NeoPixel(NUM_PIXELS, OUT_PIN, NEO_GRB + NEO_KHZ800);

// our node id
uint8_t g_node_id = 0;

// color/step information for transitions
color_t  g_color[NUM_PIXELS];
int32_t  g_brightness;

// location in space
int16_t g_pos[3];
int32_t g_angle;

// broadcast classes
const uint8_t NUM_CLASSES = 16;
const uint8_t NO_CLASS = 255;
uint8_t g_classes[NUM_CLASSES];

// calibration values
uint8_t  g_calibrate = 0; // stores the duration of the calibration in seconds
uint32_t g_calibrate_start = 0;


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

volatile uint32_t g_time = 0;
void tick(void)
{
    g_time++;
}

void reset_ticks(void)
{
    noInterrupts();
    g_time = 0;
    interrupts();
}

uint32_t ticks(void)
{
    uint32_t temp;

    noInterrupts();
    temp = g_time;
    interrupts();

    return temp; 
}

uint32_t ticks_to_ms(uint32_t ticks)
{
    return ticks * SCALE_FACTOR / g_ticks_per_sec;
}

void show_color(color_t *col)
{
    uint8_t j;
   
    for(j = 0; j < NUM_PIXELS; j++)
        set_pixel_color(j, col);

    g_pixels.show();
}

void set_pixel_color(uint8_t index, color_t *col)
{
    color_t temp;

    if (!col)
    {
        temp.c[0] = 0;
        temp.c[1] = 0;
        temp.c[2] = 0;
    }
    else
    {
        // Color correct
        temp.c[0] = pgm_read_byte(&gamma[col->c[0]]);
        temp.c[1] = pgm_read_byte(&gamma[col->c[1]]);
        temp.c[2] = pgm_read_byte(&gamma[col->c[2]]);

        // Adjust brightness
        temp.c[0] = temp.c[0] * g_brightness / SCALE_FACTOR;
        temp.c[1] = temp.c[1] * g_brightness / SCALE_FACTOR;
        temp.c[2] = temp.c[2] * g_brightness / SCALE_FACTOR;
    }

    g_pixels.setPixelColor(index, temp.c[0], temp.c[1], temp.c[2]);
    g_color[index] = temp;
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
    if (target >= MAX_NODES + 1)
    {
        uint8_t cls = target - (MAX_NODES + 1), i;

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
        case PACKET_SET_ID:
            {
                if (g_node_id == NODE_ID_UNKNOWN)
                {
                    g_node_id = data[0];
                    EEPROM.write(id_address, g_node_id);
                }
                break;
            }

        case PACKET_CLEAR_ID:
            {
                g_node_id = NODE_ID_UNKNOWN;
                EEPROM.write(id_address, g_node_id);
                break;
            }
            
        case PACKET_SINGLE_COLOR:
            {
                color_t col;
                col.c[0] = data[0];
                col.c[1] = data[1];
                col.c[2] = data[2];

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
                g_pattern_active = 0;

                // reset the heap, thereby destroying the previous patten object
                heap_setup(g_heap);

                if (parse_packet(data, len - 2, &g_pattern))
                {
                    dprintf("parse ok\n");
                    g_have_valid_pattern = 1;
                }                    
                break;  
            }

        case PACKET_START:
            {
                dprintf("Received start\n");
                start_pattern();
                break;
            }
            
        case PACKET_OFF:
            {
                g_pattern_active = 0;
                g_error = ERR_OK;
                g_target = 0;
                set_brightness(1000);
                show_color(NULL);
            }
            break;
            
        case PACKET_ENTROPY:
            {
                color_t col;

                g_random_seed = *(int32_t *)data;
                randomSeed(g_random_seed);
                show_color(NULL);
            }
            break;  

        case PACKET_DELAY:
            g_delay = data[0];
            break;  

        case PACKET_SPEED:
            g_speed = *(uint16_t *)data;
            break;  
            
        case PACKET_POSITION:
        { 
            g_pos[0] = *(uint16_t *)data;
            g_pos[1] = *(uint16_t *)(&data[2]);
            g_pos[2] = *(uint16_t *)(&data[4]);
            break;       
        }

        case PACKET_ANGLE:
        { 
            g_angle = *(uint32_t *)data;
            break;       
        }

        case PACKET_CLASSES:
            {
                uint8_t i;

                for(i = 0; i < NUM_CLASSES; i++)
                    g_classes[i] = NO_CLASS;

                for(i = 0; i < len - 2; i++)
                    g_classes[i] = data[i];

                break;
            }
        case PACKET_CALIBRATE:
            {  
                color_t col;

                col.c[1] = col.c[2] = 0;
                col.c[0] = 255;

                // clear out any stray characters
                while(Serial.available() > 0) 
                    Serial.read();

                show_color(&col);
                reset_ticks();
                g_calibrate = data[0];
                g_calibrate_start = 0;
                break;
            }
        case PACKET_BRIGHTNESS:
            {
                int32_t b;
                b = (int32_t)data[0] * 10;
                set_brightness(b);
                break;
            }
        default:
            dprintf("Invalid packet received\n");
    }
}

#if 0
void print_col(color_t *c)
{
    Serial.print(c->c[0], DEC);
    Serial.print(", ");
    Serial.print(c->c[1], DEC);
    Serial.print(", ");
    Serial.println(c->c[2], DEC);
}
#endif

void set_brightness(int32_t brightness)
{
    g_brightness = brightness;
}

void start_pattern(void)
{
    uint8_t  i;
    color_t     color;

    if (!g_have_valid_pattern)
        return;

    reset_ticks();
    g_target = g_ticks_per_frame;
    g_error = ERR_OK;
    g_pattern_active = 1;
    g_have_valid_pattern = 0;

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

    if (!g_pattern_active)
        return;

    if (g_target && ticks() >= g_target)
    {
        g_target += g_ticks_per_frame;
        g_pixels.show();

        for(i = 0; i < NUM_PIXELS; i++)
        {
            color = g_color[i];
            evaluate(&g_pattern, ticks_to_ms(g_target), i, &color);
            set_pixel_color(i, &color);
        }
    }
}

void error_pattern(void)
{
    uint8_t  t;
    uint8_t  i;
    color_t  col;

    t = ticks_to_ms(ticks()) % (ERROR_DELAY * 2);
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

#define MAX 80 
void dprintf(const char *fmt, ...)
{
    va_list va;
    va_start (va, fmt);

    char buffer[MAX];
    char *ptr = buffer;
    vsnprintf(buffer, MAX, fmt, va);
    va_end (va);

    for(ptr = buffer; *ptr; ptr++)
    {
       if (*ptr == '\n') 
           Serial.write('\r');
       Serial.write(*ptr);
    }
}

void setup()
{ 
    uint32_t timer_cal;
    color_t col;
    uint8_t i;

    Serial.begin(38400);
    Serial.println("hue-chandelier board!\n");

    g_pixels.begin();
    startup_animation();
        
    g_node_id = EEPROM.read(id_address);

    EEPROM.get(calibration_address, timer_cal);
    if (timer_cal > 1 && timer_cal != 0xFFFF)
    {
        g_ticks_per_sec = timer_cal;
        Serial.print("calibrated " + String(timer_cal) + " ");
        col.c[0] = 0;
        col.c[1] = 128;
        col.c[2] = 0;
    }
    else
    {
        col.c[0] = 0;
        col.c[1] = 0;
        col.c[2] = 128;
    }
    if (g_node_id == 0 || g_node_id >= MAX_NODES)
    {
        col.c[0] = 128;
        col.c[1] = 0;
        col.c[2] = 0;
    }
    show_color(&col);

    Serial.println("node " + String(g_node_id) + " ready. ");

    g_ticks_per_frame = g_ticks_per_sec * g_delay / 1000;

    memset(&g_pattern, 0, sizeof(pattern_t));
    memset(&g_color, 0, sizeof(g_color));

    Timer1.initialize(US_PER_TICK);
    Timer1.attachInterrupt(tick);
    
    for(i = 0; i < NUM_CLASSES; i++)
        g_classes[i] = NO_CLASS;

}

void loop()
{
    uint8_t            i, ch, data[3];
    static uint8_t     found_header = 0;
    static uint16_t    crc = 0, len = 0, recd = 0;
    
    if (g_calibrate)
    {
        if (Serial.available() > 0 && g_calibrate_start == 0)
        {
             noInterrupts();
             g_calibrate_start = g_time;
             interrupts();
             Serial.read();
             
             return;
        }
        if (Serial.available() > 0 && g_calibrate_start > 0)
        {
             int32_t done, ticks_per_sec;
             noInterrupts();
             done = (int32_t)g_time;
             interrupts();
             
             show_color(NULL);

             g_ticks_per_sec = (done - g_calibrate_start) / g_calibrate;
             g_ticks_per_frame = g_ticks_per_sec * g_delay / 1000;
             EEPROM.put(calibration_address, g_ticks_per_sec);
             
             Serial.read();
                       
             g_calibrate = 0;
             g_calibrate_start = 0;
             
             return;
        }
        return;
    }
    
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
