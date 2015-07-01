#include <avr/io.h>
#include <avr/interrupt.h>

// Bit manipulation macros
#define sbi(a, b) ((a) |= 1 << (b))       //sets bit B in variable A
#define cbi(a, b) ((a) &= ~(1 << (b)))    //clears bit B in variable A
#define tbi(a, b) ((a) ^= 1 << (b))       //toggles bit B in variable A

void repeat_pin(void)
{
    uint8_t      state;

    state = PINB & (1<<PINB2);
    if (state)
        sbi(PORTB, 4);
    else
        cbi(PORTB, 4);
}

ISR(INT0_vect)
{
    repeat_pin();
}

int main (void)
{
    DDRB |= (1<< PORTB4);

    // interrupt on INT0 on any change
    MCUCR |= (1<<ISC00);

    // turn on the INT0 interrupt
    GIMSK  |= (1<<INT0);

    //check the current state and set the output accordingly
    repeat_pin();

    // Turn on global interrupts and go!
    sei();

    for(;;)
        ; // la die dah. fuck all to do! 

    return 0;
}
