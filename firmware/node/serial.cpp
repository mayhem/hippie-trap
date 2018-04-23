#include <avr/io.h>
#include <avr/interrupt.h>
#include "serial.h"

const uint8_t g_circular_buffer_size = 32;
volatile uint8_t g_circular_buffer[g_circular_buffer_size];
volatile uint8_t g_circular_buffer_start = 0;
volatile uint8_t g_circular_buffer_end = 0;

ISR(USART_RX_vect)
{
    uint8_t ch, next = (g_circular_buffer_start+1) % g_circular_buffer_size;
            
    ch = _UDR;
    if (next == g_circular_buffer_end)
        return;

    g_circular_buffer[g_circular_buffer_start] = ch;
    g_circular_buffer_start = next;
}

void serial_init(void)
{
    // UART 0
    /*Set baud rate */ 
    _UBRRH = (unsigned char)(UBBR>>8); 
    _UBRRL = (unsigned char)UBBR; 

    /* Enable usart */ 
    _UCSRB = (1<<_TXEN)|(1<<_RXEN)|(1<<RXCIE0);
    /* Set frame format: 8data, 1stop bit */ 
    _UCSRC = (0<<_USBS)|(3<<_UCSZ0); 
}

void serial_tx(uint8_t ch)
{
    while ( !( _UCSRA & (1<<_UDRE)) )
        ;

    _UDR = ch;
}

uint8_t serial_char_ready(void)
{
    uint8_t circular_buffer_start, circular_buffer_end;

    cli();
    circular_buffer_start = g_circular_buffer_start;
    circular_buffer_end = g_circular_buffer_end;
    sei();

    return circular_buffer_start != circular_buffer_end;
}

uint8_t serial_rx(void)
{
    uint8_t ch;

    while (!serial_char_ready() )
        ;

    cli();
    ch = g_circular_buffer[g_circular_buffer_end];
    g_circular_buffer_end = (g_circular_buffer_end+1) % g_circular_buffer_size;
    sei();

    return ch;
}

#if 1
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
#endif
