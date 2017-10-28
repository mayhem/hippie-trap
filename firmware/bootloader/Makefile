CC=avr-gcc
CFLAGS=-g -Os -Wall -I../common -mcall-prologues -mmcu=atmega328p -DF_CPU=8000000UL
OBJ2HEX=avr-objcopy 
TARGET=bootloader
LDFLAGS = -Wl,-Map,$(TARGET).map,-Ttext=0x7000

program: $(TARGET).hex 
	sudo avrdude -v -p m328p -P usb -c avrispmkII -Uflash:w:$(TARGET).hex -B 1.0

fuses:
        # Use the bootloader
	sudo avrdude -p m328p -P usb -c avrispmkII -U lfuse:w:0xe2:m -U hfuse:w:0xd0:m -U efuse:w:0xff:m -U lock:w:0xEF:m -B 8
 
        # without bootloader
        # sudo avrdude -p m328p -P usb -c avrispmkII -U lfuse:w:0xe2:m -U hfuse:w:0xd1:m -U efuse:w:0xff:m -B 8

$(TARGET).o: $(TARGET).c
	$(CC) $(CFLAGS) -c $(TARGET).c 

$(TARGET).hex: $(TARGET).obj
	$(OBJ2HEX) -R .eeprom -O ihex $< $@

$(TARGET).obj: $(TARGET).o 
	$(CC) $(CFLAGS) -o $@ $(LDFLAGS) $(TARGET).o 

clean:
	rm -f *.hex *.obj *.o *.map
