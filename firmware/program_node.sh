#!/bin/sh

./fuses.sh
sleep 3
./generate_node_id.py id.raw
avrdude -p m328p -P usb -c avrispmkII -U eeprom:w:id.raw:r
rm -f id.raw
sleep 1
avrdude -p m328p -P usb -c avrispmkII -Uflash:w:$1
