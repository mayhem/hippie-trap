#!/bin/sh

./fuses.sh
#sleep 1
./generate_node_id.py id.raw
sudo avrdude -p m328p -P usb -c avrispmkII -U eeprom:w:id.raw:r
rm -f id.raw
#sleep 1
sudo avrdude -p m328p -P usb -c avrispmkII -Uflash:w:$1
echo "finished programming node:"
cat last_node_id.txt
