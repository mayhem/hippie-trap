CC=avr-gcc
CFLAGS=-g -Os -Wall -I../common -mcall-prologues -mmcu=atmega328p -DF_CPU=8000000UL
OBJ2HEX=avr-objcopy 
TARGET=test
LDFLAGS = -Wl,-Map,$(TARGET).map

program: $(TARGET).hex 
	sudo avrdude -v -D -p m328p -P usb -c avrispmkII -Uflash:w:$(TARGET).hex -B 1.0

$(TARGET).o: $(TARGET).c
	$(CC) $(CFLAGS) -c $(TARGET).c 

$(TARGET).hex: $(TARGET).obj
	$(OBJ2HEX) -R .eeprom -O ihex $< $@

$(TARGET).obj: $(TARGET).o 
	$(CC) $(CFLAGS) -o $@ $(LDFLAGS) $(TARGET).o 

clean:
	rm -f *.hex *.obj *.o *.map
