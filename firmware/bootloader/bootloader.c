#include <avr/io.h>
#include <util/delay.h>
#include <stdio.h>
#include <stdarg.h>
#include <avr/interrupt.h>
#include <avr/boot.h>
#include <avr/wdt.h>
#include <avr/pgmspace.h>
#include <avr/eeprom.h>
#include "ws2812.h"


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

void set_color(uint8_t r, uint8_t g, uint8_t b)
{
    uint8_t col[3];

    col[0] = g;
    col[1] = r;
    col[2] = b;
    ws2812_sendarray(col, 3);
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
#define ee_program_version_offset     2

// LED color codes
// green - entered bootloader as request, waiting to be programmed
// red   - no valid program, waiting to be programmed

int main() 
{
    uint8_t start_program;
    uint8_t have_valid_program;
//    uint32_t program_version;
    enum response_t response;

    // To force entering the bootloader
    //eeprom_write_byte((uint8_t *)ee_start_program_offset, 0);
    //eeprom_write_byte((uint8_t *)ee_have_valid_program_offset, 0);
    //eeprom_busy_wait();

    set_output(DDRD, LED);

    serial_init();
    dprintf("bootloader\n");

    start_program = eeprom_read_byte((const uint8_t *)ee_start_program_offset); 
    have_valid_program = eeprom_read_byte((const uint8_t *)ee_have_valid_program_offset); 
    dprintf("start: %d valid: %d\n", start_program, have_valid_program);
//    program_version = eeprom_read_dword((const uint32_t *)ee_program_version_offset); 
    eeprom_busy_wait();

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
            set_color(255, 0, 0);
            dprintf("no valid program. ready.\n");
        }
        else
        {
            set_color(0, 255, 0);
            dprintf("entered bootloader. ready.\n");
        }

        response = RSP_OK;
        while (response != RSP_FINISHED)
        {
            response = process_line();
            if (response == RSP_OK)
                ; //dprintf("ok\n");
            else 
            if (response != RSP_FINISHED)
                break;
        }   

        if (response == RSP_FINISHED)
        {
            dprintf("programmed ok.\n");
            set_color(0, 255, 0);
            _delay_ms(500);
            set_color(0, 0, 0);

            boot_spm_busy_wait();
            eeprom_write_byte((uint8_t *)ee_start_program_offset, 1);
            eeprom_write_byte((uint8_t *)ee_have_valid_program_offset, 0);
            eeprom_busy_wait();

            boot_rww_enable ();
            asm("jmp 0000");
        }
        else
        {
            dprintf("fail");
            set_color(255, 0, 0);
            _delay_ms(500);
            set_color(0, 0, 0);
        }

        dprintf("reset!\n");

        boot_rww_enable ();
        wdt_reset();
        while(1) 
            ;
    }

    return 0;
}
