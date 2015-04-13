# led-chandelier
LED bottle chandelier built for Nowhere 2015

by Robert Kaye and David Martin


Mock-up
=======

For a render of what we think this might look like a look in the design folder.

Hardware notes
==============

The chandalier made up of about 100 bottles that will have circuit boards with LEDs
inside them. 4 RGD LEDs (WS2812B) connected to an atmega128 will light up each bottle.
Communication happens over a bone simple serial connection, hopefully at 250kbps.
For serial timing and ram reasons, I chose the atmega128 over the attiny84.

The bottles will be connected to 5V power, ground and a communication line. The communication
will be via a line driver that broadcasts the serial signal to each bottle. The RPi can then
send either color information to each bottle or more interestingly send a crude set of instructions
on how to build a color animation. This way the chanelier can work in a centrally coordinated
mode or each bottle carrying out its own program.

.brd and .sch files for Eagle are in hardware folder.

Notes about the circuit
-----------------------

- Regulated 5V power supply in the body of the chandelier
- WS2812B LEDS: http://www.adafruit.com/datasheets/WS2812B.pdf
- MCU: atmega168
- Shottky diodes on the inputs.
- Program via a pogoplug, no actual connector will be on the board.
