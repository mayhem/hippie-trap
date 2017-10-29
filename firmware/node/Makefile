CC=avr-gcc
CFLAGS=-g -Os -Wall -I../common -mcall-prologues -mmcu=atmega328p -DF_CPU=8000000UL
OBJ2HEX=avr-objcopy 
TARGET=node
LDFLAGS = -Wl,-Map,$(TARGET).map

hex: $(TARGET).hex

program: $(TARGET).hex 
	sudo avrdude -v -D -p m328p -P usb -c avrispmkII -Uflash:w:$(TARGET).hex 

$(TARGET).o: $(TARGET).cpp
	$(CC) $(CFLAGS) -c $(TARGET).cpp 

function.o: function.cpp function.h
	$(CC) $(CFLAGS) -c function.cpp

serial.o: serial.cpp serial.h
	$(CC) $(CFLAGS) -c serial.cpp

parse.o: parse.cpp parse.h
	$(CC) $(CFLAGS) -c parse.cpp

sin_table.o: sin_table.cpp sin_table.h
	$(CC) $(CFLAGS) -c sin_table.cpp

ws2812.o: ws2812.cpp ws2812.h
	$(CC) $(CFLAGS) -c ws2812.cpp

$(TARGET).hex: $(TARGET).obj
	$(OBJ2HEX) -R .eeprom -O ihex $< $@

$(TARGET).obj: $(TARGET).o ws2812.o function.o serial.o parse.o sin_table.o
	$(CC) $(CFLAGS) -o $@ $(LDFLAGS) $(TARGET).o ws2812.o function.o serial.o parse.o sin_table.o

clean:
	rm -f *.hex *.obj *.o *.map
