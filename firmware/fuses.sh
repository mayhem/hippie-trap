#!/bin/sh

#avrdude -p m328p -P usb -c avrispmkII -U lfuse:w:0xe2:m -U hfuse:w:0xD1:m -U efuse:w:0xff:m -B 8
avrdude -p m328p -P usb -c avrispmkII -U lfuse:w:0xe2:m -U hfuse:w:0xd1:m -U efuse:w:0xff:m
