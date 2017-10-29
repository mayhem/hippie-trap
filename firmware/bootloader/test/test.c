#include <avr/io.h>
#include <util/delay.h>
#include <stdio.h>
#include <stdarg.h>
#include <avr/interrupt.h>
#include <avr/eeprom.h>
#include "ws2812.h"

#define BAUD 38400
#define UBBR (F_CPU / 16 / BAUD - 1)

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

#define output_low(port,pin) port &= ~(1<<pin)
#define output_high(port,pin) port |= (1<<pin)
#define set_input(portdir,pin) portdir &= ~(1<<pin)
#define set_output(portdir,pin) portdir |= (1<<pin)

void set_color(uint8_t r, uint8_t g, uint8_t b)
{
    uint8_t col[3];

    col[0] = g;
    col[1] = r;
    col[2] = b;
    ws2812_sendarray(col, 3);
}

#define LED PD2

#define ee_have_valid_program_offset  1

int main() 
{
    set_output(DDRD, LED);

    serial_init();
    dprintf("\ntest program running\n");
    eeprom_write_byte((uint8_t *)ee_have_valid_program_offset, 1);

    for(;;)
    {
        set_color(255, 0, 255);
        _delay_ms(500);
        set_color(255, 128, 0);
        _delay_ms(500);
    }

    return 0;
}
