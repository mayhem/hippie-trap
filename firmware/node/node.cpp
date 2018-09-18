#include <util/crc16.h>
#include <avr/pgmspace.h>
#include <avr/wdt.h>
#include <avr/eeprom.h>
#include <stdarg.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <string.h>
#include "ws2812.h"
#include "serial.h"
#include "function.h"
#include "colorspace.h"

const uint8_t NODE_ID_UNKNOWN = 255;
const uint8_t MAX_NODES = 127;
const uint8_t LED_PIN = 2;
const uint8_t US_PER_TICK = 25;
#define TIMER1_INIT      0xFFF8
#define TIMER1_FLAGS     _BV(CS12)|(1<<CS10); // 8Mhz / 1024 / 8 = .001024 per tick


const uint16_t MAX_PACKET_LEN     = 128;
const uint8_t BROADCAST = 0;
const uint8_t PACKET_SINGLE_LED   = 1; 
const uint8_t PACKET_SINGLE_COLOR = 2; 
const uint8_t PACKET_COLOR_ARRAY  = 3; 
const uint8_t PACKET_PATTERN      = 4; 
const uint8_t PACKET_ENTROPY      = 5; 
const uint8_t PACKET_START        = 6; 
const uint8_t PACKET_CLEAR        = 7; 
const uint8_t PACKET_STOP         = 8; 
const uint8_t PACKET_DELAY        = 10;
const uint8_t PACKET_ADDR         = 11;
const uint8_t PACKET_SPEED        = 12;
const uint8_t PACKET_CLASSES      = 13;
const uint8_t PACKET_CALIBRATE    = 14;
const uint8_t PACKET_BRIGHTNESS   = 15;
const uint8_t PACKET_BOOTLOADER   = 17;
const uint8_t PACKET_RESET        = 18;
const uint8_t PACKET_RANDOM_COLOR = 19;

// where in EEPROM our node id is stored. The first 16 are reserved for the bootloader
// Bootloader items
const uint8_t ee_valid_program_offset  = 0;
const uint8_t ee_init_ok_offset        = 1;

// Node items
const uint8_t ee_id_offset                  = 16;
const uint8_t ee_calibration_offset         = 17;

// ----- globals ------------
uint8_t    g_error = ERR_OK;

// time keeping
uint8_t    g_delay = 20;
uint32_t   g_speed = SCALE_FACTOR;
uint32_t   g_ticks_per_sec = (int32_t)1000000 / US_PER_TICK;
uint32_t   g_ticks_per_frame; // setup later
uint32_t   g_target = 0;

// led/scaled color buffer
uint8_t    COLOR_SHIFT = 7;
color32_t  g_color_buffer[NUM_LEDS];
color_t    g_led_buffer[NUM_LEDS];
uint8_t    g_brightness = 100;

// random seed
uint32_t    g_random_seed = 0;

// pattern, packet
uint8_t     g_packet[MAX_PACKET_LEN];
uint8_t     g_pattern_data[MAX_PACKET_LEN];
uint8_t     g_pattern_data_len = 0;

// our node id
uint8_t g_node_id = 0;

// broadcast groups
const uint8_t NUM_GROUPS = 16;
const uint8_t NO_GROUP = 255;
uint8_t g_groups[NUM_GROUPS];

// calibration values
uint8_t  g_calibrate = 0; // stores the duration of the calibration in seconds
uint32_t g_calibrate_start = 0;

// ---- prototypes -----
void set_brightness(int32_t brightness);

volatile uint32_t g_time = 0;
volatile uint32_t g_global = 0;
ISR (TIMER1_OVF_vect)
{
    g_time++;
    g_global++;
    TCNT1 = TIMER1_INIT;
}

void reset_ticks(void)
{
    cli();
    g_time = 0;
    sei();
}

uint32_t ticks(void)
{
    uint32_t temp;

    cli();
    temp = g_time;
    sei();

    return temp; 
}

uint32_t ticks_to_ms(uint32_t ticks)
{
    return ticks * SCALE_FACTOR / g_ticks_per_sec;
}

void update_leds(void)
{
    ws2812_sendarray((uint8_t *)g_led_buffer, 3 * NUM_LEDS);
}

void clear_led(uint8_t index)
{
    g_color_buffer[index].r = 0;
    g_color_buffer[index].g = 0;
    g_color_buffer[index].b = 0;
    g_led_buffer[index].r = 0;
    g_led_buffer[index].g = 0;
    g_led_buffer[index].b = 0;
}

void get_led(uint8_t index, color_t *col)
{
    *col = g_led_buffer[index];
}

void set_led(uint8_t index, color_t *col)
{
    g_color_buffer[index].r = col->r << COLOR_SHIFT;
    g_color_buffer[index].g = col->g << COLOR_SHIFT;
    g_color_buffer[index].b = col->b << COLOR_SHIFT;

    g_led_buffer[index].r = ((g_color_buffer[index].r * g_brightness / 100) >> COLOR_SHIFT) & 0xFF;
    g_led_buffer[index].g = ((g_color_buffer[index].g * g_brightness / 100) >> COLOR_SHIFT) & 0xFF;
    g_led_buffer[index].b = ((g_color_buffer[index].b * g_brightness / 100) >> COLOR_SHIFT) & 0xFF;
}

void set_led_rgb(uint8_t index, uint8_t r, uint8_t g, uint8_t b)
{
    color_t temp;

    temp.r = r;
    temp.g = g;
    temp.b = b;
    set_led(index, &temp);
}

void set_brightness(int32_t brightness)
{
    g_brightness = brightness;
}

// Delta is a % of change. 0 = off, 50% half brightness, 100 no change, 200 twice is bright.
void adjust_led_brightness(uint8_t delta)
{
    uint8_t  i;

    for(i = 0; i < NUM_LEDS; i++)
    {
        g_color_buffer[i].r = g_color_buffer[i].r * delta / 100;
        g_color_buffer[i].g = g_color_buffer[i].g * delta / 100;
        g_color_buffer[i].b = g_color_buffer[i].b * delta / 100;

        g_led_buffer[i].r = (g_color_buffer[i].r >> COLOR_SHIFT) & 0xFF;
        g_led_buffer[i].g = (g_color_buffer[i].g >> COLOR_SHIFT) & 0xFF;
        g_led_buffer[i].b = (g_color_buffer[i].b >> COLOR_SHIFT) & 0xFF;
    }
    update_leds();
}

void set_color(color_t *col)
{
    uint8_t j;

    for(j = 0; j < NUM_LEDS; j++)
        set_led(j, col);

    update_leds();
}

void clear_color(void)
{
    uint8_t j;

    for(j = 0; j < NUM_LEDS; j++)
        clear_led(j);

    update_leds();
}

void set_color_rgb(uint8_t r, uint8_t g, uint8_t b)
{
    uint8_t j;
    color_t col;

    col.r = r;
    col.g = g;
    col.b = b;
   
    for(j = 0; j < NUM_LEDS; j++)
        set_led(j, &col);

    update_leds();
}

uint16_t flash_animation(color_t *col1, color_t *col2)
{
    uint8_t i, j, d;
    uint16_t force_bl_count = 0;

    for(i = 0; i < 10; i++)
    {       
        for(j = 0; j < NUM_LEDS; j++)
        {
            if (i % 2 == 0)
            {
                if (j % 2 == 1)
                    set_led(j, col1);
                else
                    clear_led(j);
            }
            else
            {
                if (j % 2 == 0)
                    set_led(j, col2);
                else
                    clear_led(j);  
            }
        }   

        update_leds();

        for(d=0; d < 100; d++)
        {
            if (serial_char_ready() && serial_rx() == 'M')
                force_bl_count++;

            _delay_ms(1);
        }
    }
    clear_color();

    return force_bl_count;
}

uint16_t startup_animation(void)
{
    color_t col1, col2;

    col1.r = 255;
    col1.g = 140;
    col1.b = 0;
    col2.r = 255;
    col2.g = 0;
    col2.b = 255;
    return flash_animation(&col1, &col2);
}

uint16_t error_animation(void)
{
    color_t col1, col2;

    col1.r = 128;
    col1.g = 0;
    col1.b = 0;
    col2.r = 128;
    col2.g = 128;
    col2.b = 128;
    return flash_animation(&col1, &col2);
}

void update_pattern(void)
{
    if (g_target && ticks() >= g_target)
    {
        update_leds();

        apply_pattern(ticks(), g_pattern_data, g_pattern_data_len);
        g_target += g_ticks_per_frame;
    }
}

void start_pattern(void)
{
    reset_ticks();
    g_target = g_ticks_per_frame;
    apply_pattern(0, g_pattern_data, g_pattern_data_len);
    update_pattern();  
}    

void stop_pattern(void)
{
    g_target = 0;
}    

void reset(void)
{
    cli();

    void *bl = (void *) 0x7000;
    goto *bl;

    for(;;)
        ;
}

void enter_bootloader(void)
{
    eeprom_write_byte((uint8_t *)ee_valid_program_offset, 0);
    eeprom_write_byte((uint8_t *)ee_init_ok_offset, 0);
    eeprom_busy_wait();

    set_color_rgb(255, 0, 0);
    _delay_ms(1000);
    clear_color();
    reset();
}

void handle_packet(uint16_t len, uint8_t *packet)
{
    uint8_t    type, target, i;
    uint8_t   *data;

    target = packet[0];
    if (target > MAX_NODES)
    {
        uint8_t group = target & 0x7F;

        for(i = 0; i < NUM_GROUPS; i++)
            if (g_groups[i] == group)
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
                col.r = data[0];
                col.g = data[1];
                col.b = data[2];

                for(int j=0; j < NUM_LEDS; j++)
                    set_color(&col);

                break;
            } 

        case PACKET_SINGLE_LED:
            {
                color_t col;
                uint8_t led;

                led = data[1];
                col.r = data[1];
                col.g = data[2];
                col.b = data[3];

                set_led(led, &col);
                break;
            } 

        case PACKET_COLOR_ARRAY:
            {
                color_t col;

                for(int j=0; j < NUM_LEDS; j++, data += 3)
                {
                    col.r = data[0];
                    col.g = data[1];
                    col.b = data[2];
                    set_led(j, &col);
                }
                update_leds();
                break;  
            }

        case PACKET_PATTERN:
            {
                memcpy(g_pattern_data, data, len - 2); 
                g_pattern_data_len = len - 2;
                break;  
            }

        case PACKET_START:
            {
                start_pattern();
                break;
            }

        case PACKET_STOP:
            {
                stop_pattern();
                break;
            }
            
        case PACKET_CLEAR:
            {
                stop_pattern();
                clear_color();
            }
            break;
            
        case PACKET_ENTROPY:
            {
                g_random_seed = *(int32_t *)data;
                srand(g_random_seed);
            }
            break;  

        case PACKET_DELAY:
            g_delay = data[0];
            break;  

        case PACKET_SPEED:
            g_speed = *(uint16_t *)data;
            break;  
            
        case PACKET_CLASSES:
        {
            uint8_t i;

            for(i = 0; i < NUM_GROUPS; i++)
                g_groups[i] = NO_GROUP;

            for(i = 0; i < len - 2; i++)
            {  
                g_groups[i] = data[i];
            }
            break;
        }
        case PACKET_CALIBRATE:
        {  
            color_t col;

            col.g = col.b = 0;
            col.r = 255;

            // clear out any stray characters
            while(serial_char_ready()) 
                serial_rx();

            set_color(&col);
            reset_ticks();
            g_calibrate = data[0];
            g_calibrate_start = 0;
            break;
        }
        case PACKET_BRIGHTNESS:
        {
            set_brightness(data[0]);
            break;
        }
        case PACKET_BOOTLOADER:
        {
            enter_bootloader();
            break;
        }
        case PACKET_RESET:
        {
            reset();
        }
        case PACKET_RANDOM_COLOR:
        {
            color_t col;

            hsv_to_rgb(rand() % SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR, &col);
            set_color(&col);
            break;
        }
        default:
            return;
    }
}

#define output_low(port,pin) port &= ~(1<<pin)
#define output_high(port,pin) port |= (1<<pin)
#define set_input(portdir,pin) portdir &= ~(1<<pin)
#define set_output(portdir,pin) portdir |= (1<<pin)

void loop()
{
    uint8_t            ch;
    static uint8_t     found_header = 0;
    static uint16_t    crc = 0, len = 0, recd = 0;

    if (g_calibrate)
    {
        if (serial_char_ready() && g_calibrate_start == 0)
        {
             cli();
             g_calibrate_start = g_time;
             sei();
             serial_rx();
             
             return;
        }
        if (serial_char_ready() > 0 && g_calibrate_start > 0)
        {
             int32_t done;
             cli();
             done = (int32_t)g_time;
             sei();
             
             clear_color();

             g_ticks_per_sec = (done - g_calibrate_start) / g_calibrate;
             g_ticks_per_frame = g_ticks_per_sec * g_delay / 1000;
             eeprom_write_dword((uint32_t *)ee_calibration_offset, g_ticks_per_sec);
             
             serial_rx();
                       
             g_calibrate = 0;
             g_calibrate_start = 0;
             
             return;
        }
        return;
    }

    update_pattern();
    
    if (serial_char_ready()) 
    {
        ch = serial_rx();
        if (found_header < 2)
        {
            if (ch == 0xBE)
                found_header = 1;
            else
            if (found_header == 1 && ch == 0xEF)
                found_header = 2;
            else
                found_header = 0;
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
                    crc = 0;
                }
                else
                {
                    // Nope, that was no header, better keep looking.
                    found_header = 0;
                }
            }
            else
            {
                g_packet[recd++] = ch;
                
                if (recd <= len - 2)
                    crc = _crc16_update(crc, ch);

                if (recd > 0 && (recd == len || recd == MAX_PACKET_LEN))
                {
                    uint16_t *pcrc;
                            
                    // if we received the right length, check the crc. If that matches, we have a packet!
                    if (recd == len)
                    {            
                        pcrc = (uint16_t *)(g_packet + len - 2);
                        if (crc == *pcrc)
                            handle_packet(len - 2, g_packet);
                        else
                            error_animation();
                    }

                    len = 0;
                    found_header = 0;
                    recd = 0;
                }
            }
        }
    }
}

int16_t sin16_avr( uint16_t theta );

#define MAX_BL_FORCE_COUNT 5
int main(void)
{ 
    uint32_t timer_cal;
    uint32_t panic_count;
    color_t col;
    uint8_t i;

    // Turn off the watchdog timer, in case we were reset that way
    MCUSR = 0;
    wdt_disable();

    TCCR1B |= TIMER1_FLAGS;
    TCNT1 = TIMER1_INIT;
    TIMSK1 |= (1<<TOIE1);

    serial_init(1);
    sei();
    dprintf("yo, hippies\n");

#if 0
    color32_t c;

    c.r = 255;
    dprintf("%u\n", c.r);
    c.r <<= COLOR_SHIFT;
    dprintf("%u\n", c.r);
    c.r = c.r * 90 / 100;
    dprintf("%u\n", c.r);
#endif

    set_output(DDRD, LED_PIN);
    panic_count = startup_animation();
    if (panic_count > MAX_BL_FORCE_COUNT)
    {
        enter_bootloader();
    }
    _delay_ms(1000);
    set_color_rgb(128, 28, 0);

    set_brightness(100);
    clear_color();

    timer_cal = eeprom_read_dword((uint32_t *)ee_calibration_offset);
    if (timer_cal > 1 && timer_cal != 0xFFFF)
    {
        g_ticks_per_sec = timer_cal;
        col.r = 0;
        col.g = 128;
        col.b = 0;
    }
    else
    {
        col.r = 0;
        col.g = 0;
        col.b = 128;
    }


    g_node_id = eeprom_read_byte((uint8_t *)ee_id_offset);
    if (g_node_id == 0 || g_node_id >= MAX_NODES)
    {
        col.r = 128;
        col.g = 0;
        col.b = 0;
    }

    set_color(&col);

    // If we received panic counts, show purple for one second.
    if (panic_count)
    {
        set_color_rgb(255, 0, 255);
        _delay_ms(1000);
    }

    g_ticks_per_frame = g_ticks_per_sec * g_delay / 1000;
    g_target = 0;

    for(i = 0; i < NUM_GROUPS; i++)
        g_groups[i] = NO_GROUP;

    // Tell the bootloader that init completed ok, if that flag isn't set.
    if (!eeprom_read_byte((uint8_t *)ee_init_ok_offset))
        eeprom_write_byte((uint8_t *)ee_init_ok_offset, 1);

    for(;;)
        loop();

    return 0;
}
