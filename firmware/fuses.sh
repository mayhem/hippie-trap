#!/bin/sh

avrdude -p t84 -P usb -c avrispmkII -U lfuse:w:0xe2:m -U lfuse:w:0xe2:m -U hfuse:w:0xd7:m -U efuse:w:0xff:m -B 8
