#ifndef SERIAL_H
#define SERIAL_H

#include <stdio.h>
#include <stdarg.h>

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

void    serial_init(void);
void    serial_tx(uint8_t ch);
uint8_t serial_char_ready();
uint8_t serial_rx();

#endif
