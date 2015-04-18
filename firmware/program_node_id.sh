#!/bin/sh

./generate_node_id.py id.raw $1
sudo avrdude -p m328p -P usb -c avrispmkII -U eeprom:w:id.raw:r
rm -f id.raw
