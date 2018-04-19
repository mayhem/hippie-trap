#include <avr/io.h>
#include <util/delay.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <avr/interrupt.h>
#include <avr/boot.h>
#include <avr/wdt.h>
#include <avr/pgmspace.h>
#include <avr/eeprom.h>
#include "ws2812.h"
#include "serial.h"

#define NUM_LEDS 4

struct cRGB g_led_rgb[NUM_LEDS];

void update_leds(void)
{
    ws2812_setleds((struct cRGB *)g_led_rgb, NUM_LEDS);
}

void set_color(uint8_t r, uint8_t g, uint8_t b)
{
    memset(g_led_rgb, 0, sizeof(g_led_rgb));
    g_led_rgb[0].r = r;    
    g_led_rgb[0].g = g;    
    g_led_rgb[0].b = b;    
    g_led_rgb[3].r = r;    
    g_led_rgb[3].g = g;    
    g_led_rgb[3].b = b;    
    update_leds();
}

void leds_off(void)
{
    memset(g_led_rgb, 0, sizeof(g_led_rgb));
    update_leds();
}

#define HEX2DEC(x)  (((x < 'A') ? ((x) - 48) : ((x) - 55)))
#define SPM_PAGEMASK ((uint32_t) ~(SPM_PAGESIZE - 1))
enum response_t {RSP_OK, RSP_CHECKSUM_FAIL, RSP_INVALID, RSP_FINISHED};

enum response_t process_line(uint16_t *hex_file_received)
{
    uint8_t c, line_buffer[80], data_buffer[32];
    uint8_t line_len = 0, data_len = 0, data_count, line_type, line_pos, data;
    uint8_t addrh, addrl, checksum, recv_checksum;
    uint16_t addr, extended_addr = 0, i;
    static uint32_t full_addr, last_addr = 0xFFFFFFFF;

    eeprom_busy_wait();
    boot_spm_busy_wait();

    c = serial_rx();
    (*hex_file_received)++;
    while (c != '\r')
    {
        if (c == ':')
            line_len = 0;
        else if (c == '\n')
            ;
        else if (c == '\0')
            ;
        else if (line_len < sizeof(line_buffer))
            line_buffer[line_len++] = c;
        c = serial_rx();
        (*hex_file_received)++;
    }

    if (line_len < 2)
        return RSP_INVALID;

    data_count = (HEX2DEC(line_buffer[0]) << 4) + HEX2DEC(line_buffer[1]);
    if (line_len != data_count * 2 + 10)
        return RSP_INVALID;

    addrh =  (HEX2DEC(line_buffer[2]) << 4) + HEX2DEC(line_buffer[3]);
    addrl =  (HEX2DEC(line_buffer[4]) << 4) + HEX2DEC(line_buffer[5]);
    addr = (addrh << 8) + addrl;
    line_type = (HEX2DEC(line_buffer[6]) << 4) + HEX2DEC(line_buffer[7]);
    line_pos = 8;
    checksum = data_count + addrh + addrl + line_type;

    for (i=0; i < data_count; i++)
    {
        data = (HEX2DEC(line_buffer[line_pos]) << 4) + HEX2DEC(line_buffer[line_pos + 1]);
        line_pos += 2;
        data_buffer[data_len++] = data;
        checksum += data;
    }

    checksum = 0xFF - checksum + 1;
    recv_checksum = (HEX2DEC(line_buffer[line_pos]) << 4) + HEX2DEC(line_buffer[line_pos + 1]);
    if (checksum != recv_checksum)
        return RSP_CHECKSUM_FAIL;

    if (line_type == 1)
    {
        if (last_addr != 0xFFFFFFFF)
        {
            serial_tx('.');
            boot_page_write (last_addr & SPM_PAGEMASK);
            boot_spm_busy_wait();
        }
        return RSP_FINISHED;
    }
    else 
    if ((line_type == 2) || (line_type == 4))
        extended_addr = (data_buffer[0] << 8) + data_buffer[1];
    else if (line_type == 0)
    {
        full_addr = ((uint32_t) extended_addr << 16) + addr;
        if ((full_addr & SPM_PAGEMASK) != (last_addr & SPM_PAGEMASK))
        {
            if (last_addr != 0xFFFFFFFF)
            {
                serial_tx('.');
                boot_page_write (last_addr & SPM_PAGEMASK);
                boot_spm_busy_wait();
            }
            boot_page_erase (full_addr);
            boot_spm_busy_wait ();
        }
        for (i=0; i < data_len; i+=2)
        {
            uint16_t w = data_buffer[i] + ((uint16_t) data_buffer[i + 1] << 8);
            boot_page_fill (full_addr + i, w);
        }
        last_addr = full_addr;
    }
    return RSP_OK;
}

#define output_low(port,pin) port &= ~(1<<pin)
#define output_high(port,pin) port |= (1<<pin)
#define set_input(portdir,pin) portdir &= ~(1<<pin)
#define set_output(portdir,pin) portdir |= (1<<pin)

#define LED PD2

#define ee_valid_program_offset  0
#define ee_init_ok_offset        1

// LED color codes
// green - entered bootloader as request, waiting to be programmed
// red   - no valid program, waiting to be programmed

int main() 
{
    uint8_t init_ok;
    uint8_t valid_program;
    uint8_t start_ch_count = 0, ch, i, step;
    uint16_t hex_file_size = 0, hex_file_received = 0, panic_count = 0;
    enum response_t response;

    // Turn off the watchdog timer, in case we were reset that way
    MCUSR = 0;
    wdt_disable();

    // To force entering the bootloader
    //eeprom_write_byte((uint8_t *)ee_start_program_offset, 0);
    //eeprom_write_byte((uint8_t *)ee_valid_program_offset, 0);
    //eeprom_busy_wait();

    set_output(DDRD, LED);

    serial_init();

    set_color(128, 0, 128);
    for(i = 0; i < 250; i++)
    {
        if (serial_char_ready())
        {
            if (serial_rx() == 'M')
                panic_count++;
        }

        _delay_ms(1);
    }
    leds_off();

    valid_program = 0;
    init_ok = 0;

    if (panic_count > 10)
        eeprom_write_byte((uint8_t *)ee_valid_program_offset, 0);
    else
    {
        eeprom_busy_wait();
        valid_program = eeprom_read_byte((const uint8_t *)ee_valid_program_offset); 
        init_ok = eeprom_read_byte((const uint8_t *)ee_init_ok_offset); 
    }

    while(1)
    {
        if (valid_program)
        {
            if (init_ok)
            {
                set_color(0, 0, 0);
                asm("jmp 0000");
                return 0;
            }
            // valid program present, but init failed.
            set_color(0, 0, 128);

            // Do not try to start the program again, if we have no valid program
            eeprom_write_byte((uint8_t *)ee_valid_program_offset, 0);
        }
        else
        {
            if (panic_count > 10)
                set_color(128, 0, 0);
            else
                set_color(0, 128, 0);
        }

        for(start_ch_count = 0; start_ch_count < 16;)
        {
            ch = serial_rx();
            if (ch == 0x45)
            {
                start_ch_count++;
                continue;
            }
            start_ch_count = 0;
        }

        // Now load the size of the program
        hex_file_size = serial_rx();
        hex_file_size |= serial_rx() << 8;
        hex_file_received = 0;

        i = 0; step = 4;
        response = RSP_OK;
        while (response != RSP_FINISHED)
        {
            response = process_line(&hex_file_received);
            if (response == RSP_OK)
            {
                set_color(0, 0, i);
                i += step;
                if (i == 0 || i == 128)
                    step = -step;
            }
            else 
            if (response != RSP_FINISHED)
                break;
        }   
        set_color(0, 0, 0);

        if (response == RSP_FINISHED && hex_file_size == hex_file_received)
        {
            dprintf("programmed ok.\n");
            set_color(0, 64, 64);
            _delay_ms(2000);
            set_color(0, 0, 0);

            boot_spm_busy_wait();
            eeprom_write_byte((uint8_t *)ee_valid_program_offset, 1);
            eeprom_write_byte((uint8_t *)ee_init_ok_offset, 0);
            eeprom_busy_wait();

            boot_rww_enable ();
            asm("jmp 0000");
        }
        else
        {
            struct cRGB led;

            boot_spm_busy_wait();
            eeprom_write_byte((uint8_t *)ee_init_ok_offset, 0);
            eeprom_write_byte((uint8_t *)ee_valid_program_offset, 0);
            eeprom_busy_wait();

            if (response == RSP_FINISHED && hex_file_size != hex_file_received)
            {
                dprintf("received incorrect file size\n");
                dprintf("rec %u of %u bytes.\n", hex_file_received, hex_file_size);
                led.r = 0; led.g = 0; led.b = 128;
            }
            else if (response == RSP_CHECKSUM_FAIL)
            {
                dprintf("checksum fail\n");
                led.r = 128; led.g = 0; led.b = 0;
            }
            else if (response == RSP_INVALID)
            {
                dprintf("upload invalid\n");
                led.r = 128; led.g = 128; led.b = 0;
            }
            else 
            {
                dprintf("other error\n");
                led.r = 128; led.g = 0; led.b = 128;
            }

            for(i = 0; i < 10; i++)
            {
                set_color(led.r, led.g, led.b);
                _delay_ms(200);
                set_color(0, 0, 0);
                _delay_ms(200);
            }
        }
        dprintf("reset!\n");

        boot_rww_enable ();
        boot_spm_busy_wait();

        wdt_enable(WDTO_15MS);
        while(1) 
            ;
    }

    return 0;
}
