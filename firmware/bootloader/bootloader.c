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

#define NUM_LEDS 4


// 38400 @ 8 Mhz. See http://wormfood.net/avrbaudcalc.php
#define UBBR 12

#define _UBRRH UBRR0H
#define _UBRRL UBRR0L
#define _UCSRB UCSR0B
#define _UCSRC UCSR0C
#define _TXEN  TXEN0
#define _RXEN  RXEN0
#define _RXC   RXC0
#define _USBS  USBS0
#define _UCSZ1 UCSZ01
#define _UCSZ0 UCSZ00
#define _UCSRA UCSR0A
#define _UDRE  UDRE0
#define _UDR   UDR0 

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

void serial_init(void)
{
    // UART 0
    /*Set baud rate */ 
    _UBRRH = (unsigned char)(UBBR>>8); 
    _UBRRL = (unsigned char)UBBR; 

    /* Enable transmitter */ 
    _UCSRB = (1<<_TXEN)|(1<<_RXEN); 
    /* Set frame format: 8data, 1stop bit */ 
    _UCSRC = (0<<_USBS)|(3<<_UCSZ0); 
}

void serial_tx(unsigned char ch)
{
    while ( !( _UCSRA & (1<<_UDRE)) )
        ;

    _UDR = ch;
}

unsigned char serial_rx(void)
{
    while ( !(_UCSRA & (1<<_RXC))) 
        ;

    return _UDR;
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
        if (*ptr == '\n') serial_tx('\r');
            serial_tx(*ptr);
    }
}

#define HEX2DEC(x)  (((x < 'A') ? ((x) - 48) : ((x) - 55)))
#define SPM_PAGEMASK ((uint32_t) ~(SPM_PAGESIZE - 1))
enum response_t {RSP_OK, RSP_CHECKSUM_FAIL, RSP_INVALID, RSP_FINISHED};

enum response_t process_line()
{
    uint8_t c, line_buffer[80], data_buffer[32];
    uint8_t line_len = 0, data_len = 0, data_count, line_type, line_pos, data;
    uint8_t addrh, addrl, checksum, recv_checksum;
    uint16_t addr, extended_addr = 0, i;
    static uint32_t full_addr, last_addr = 0xFFFFFFFF;

    eeprom_busy_wait();
    boot_spm_busy_wait();

    c = serial_rx();
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

    dprintf("check ");
    for (i=0; i < data_count; i++)
    {
        data = (HEX2DEC(line_buffer[line_pos]) << 4) + HEX2DEC(line_buffer[line_pos + 1]);
        line_pos += 2;
        data_buffer[data_len++] = data;
        checksum += data;
        dprintf("%x ", data);
    }

    checksum = 0xFF - checksum + 1;
    recv_checksum = (HEX2DEC(line_buffer[line_pos]) << 4) + HEX2DEC(line_buffer[line_pos + 1]);
    dprintf(" -- %x %x (%d bytes)\n", checksum, recv_checksum, data_len);
    if (checksum != recv_checksum)
        return RSP_CHECKSUM_FAIL;

    if (line_type == 1)
    {
        if (last_addr != 0xFFFFFFFF)
        {
            dprintf("write %p\n", last_addr & SPM_PAGEMASK);
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
                dprintf("write %p\n", last_addr & SPM_PAGEMASK);
                boot_page_write (last_addr & SPM_PAGEMASK);
                boot_spm_busy_wait();
            }
            dprintf("erase %p\n", full_addr);
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

#define ee_start_program_offset       0
#define ee_have_valid_program_offset  1

// LED color codes
// green - entered bootloader as request, waiting to be programmed
// red   - no valid program, waiting to be programmed

int main() 
{
    uint8_t start_program;
    uint8_t have_valid_program;
    uint8_t start_ch_count = 0, ch, i;
    enum response_t response;

    // Turn off the watchdog timer, in case we were reset that way
    wdt_disable();

    // To force entering the bootloader
    //eeprom_write_byte((uint8_t *)ee_start_program_offset, 0);
    //eeprom_write_byte((uint8_t *)ee_have_valid_program_offset, 0);
    //eeprom_busy_wait();

    set_output(DDRD, LED);

    serial_init();
    dprintf("bootloader\n");

    set_color(128, 0, 128);
    _delay_ms(500);
    leds_off();

    eeprom_busy_wait();
    start_program = eeprom_read_byte((const uint8_t *)ee_start_program_offset); 
    have_valid_program = eeprom_read_byte((const uint8_t *)ee_have_valid_program_offset); 
    dprintf("start: %d valid: %d\n", start_program, have_valid_program);

    while(1)
    {
        if (start_program)
        {
            if (have_valid_program)
            {
                set_color(0, 0, 0);
                dprintf("start program\n");
                asm("jmp 0000");
                return 0;
            }
            // No valid program present, but shoud've started it
            set_color(128, 128, 0);
            dprintf("no valid program. ready.\n");

            // Do not try to start the program again, if we have no valid program
            eeprom_write_byte((uint8_t *)ee_start_program_offset, 0);
        }
        else
        {
            set_color(0, 0, 128);
            dprintf("entered bootloader. ready.\n");
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

        i = 0;
        response = RSP_OK;
        while (response != RSP_FINISHED)
        {
            response = process_line();
            if (response == RSP_OK)
            {
                if (i % 2 == 0)
                    set_color(0, 0, 128);
                else
                    set_color(128, 0, 0);
                i++;
            }
            else 
            if (response != RSP_FINISHED)
                break;
        }   
        set_color(0, 0, 0);

        if (response == RSP_FINISHED)
        {
            dprintf("programmed ok.\n");
            set_color(0, 128, 128);
            _delay_ms(2000);
            set_color(0, 0, 0);

            boot_spm_busy_wait();
            eeprom_write_byte((uint8_t *)ee_start_program_offset, 1);
            eeprom_write_byte((uint8_t *)ee_have_valid_program_offset, 1);
            eeprom_busy_wait();

            boot_rww_enable ();
            asm("jmp 0000");
        }
        else
        {
            struct cRGB led;

            boot_spm_busy_wait();
            eeprom_write_byte((uint8_t *)ee_start_program_offset, 0);
            eeprom_write_byte((uint8_t *)ee_have_valid_program_offset, 0);
            eeprom_busy_wait();

            if (response == RSP_CHECKSUM_FAIL)
            {
                dprintf("checksum fail");
                led.r = 128; led.g = 0; led.b = 0;
            }
            else if (response == RSP_INVALID)
            {
                dprintf("upload invalid");
                led.r = 0; led.g = 128; led.b = 0;
            }
            else 
            {
                dprintf("other error");
                led.r = 0; led.g = 0; led.b = 128;
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
