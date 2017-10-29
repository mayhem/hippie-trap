CC=avr-gcc
CFLAGS=-g -Os -Wall -I../common -mcall-prologues -mmcu=atmega328p -DF_CPU=8000000UL
OBJ2HEX=avr-objcopy 
TARGET=test
LDFLAGS = -Wl,-Map,$(TARGET).map

program: $(TARGET).hex 
	sudo avrdude -v -D -p m328p -P usb -c avrispmkII -Uflash:w:$(TARGET).hex -B 8

$(TARGET).o: $(TARGET).c
	$(CC) $(CFLAGS) -c $(TARGET).c 

ws2812.o: ws2812.c ws2812.h
	$(CC) $(CFLAGS) -c ws2812.c

$(TARGET).hex: $(TARGET).obj
	$(OBJ2HEX) -R .eeprom -O ihex $< $@

$(TARGET).obj: $(TARGET).o ws2812.o
	$(CC) $(CFLAGS) -o $@ $(LDFLAGS) $(TARGET).o ws2812.o

clean:
	rm -f *.hex *.obj *.o *.map
