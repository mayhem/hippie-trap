CC=avr-gcc
CFLAGS=-g -Os -Wall -I../common -mcall-prologues -mmcu=atmega328p -DF_CPU=8000000UL
OBJ2HEX=avr-objcopy 
TARGET=bootloader
LDFLAGS = -Wl,-Map,$(TARGET).map,-Ttext=0x7000

program: $(TARGET).hex 
	dd if=/dev/zero of=/tmp/eeprom.bin bs=1c count=2 
	sudo avrdude -e -p m328p -P usb -c avrispmkII -B 1 -Uflash:w:$(TARGET).hex -U eeprom:w:/tmp/eeprom.bin:r
	rm -f /tmp/eeprom.bin

fuses:
        # Use the bootloader
	sudo avrdude -p m328p -P usb -c avrispmkII -B 8 -U lfuse:w:0xe2:m -U hfuse:w:0xd0:m -U efuse:w:0xff:m 
 
nobootloader:
        # without bootloader
	sudo avrdude -p m328p -P usb -c avrispmkII -B 8 -U lfuse:w:0xe2:m -U hfuse:w:0xd1:m -U efuse:w:0xff:m 
	sudo avrdude -v -p m328p -P usb -c avrispmkII -Uflash:w:$(TARGET).hex -B 1.0

$(TARGET).o: $(TARGET).c
	$(CC) $(CFLAGS) -c $(TARGET).c 

ws2812.o: ws2812.c ws2812.h
	$(CC) $(CFLAGS) -c ws2812.c

serial.o: serial.c serial.h
	$(CC) $(CFLAGS) -c serial.c

$(TARGET).hex: $(TARGET).obj
	$(OBJ2HEX) -R .eeprom -O ihex $< $@

$(TARGET).obj: $(TARGET).o ws2812.o serial.o
	$(CC) $(CFLAGS) -o $@ $(LDFLAGS) $(TARGET).o ws2812.o serial.o

clean:
	rm -f *.hex *.obj *.o *.map
