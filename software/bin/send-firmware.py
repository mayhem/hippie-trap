#!/usr/bin/env python3

import sys
import os
import struct
from hippietrap import HippieTrap, BROADCAST

import click
from time import sleep

BAUD_RATE = 38400
MAX_SIZE = 0x7000

@click.command()
@click.argument('filename')
def send_firmware(filename):
    with HippieTrap() as ch:
        try:
            with open(filename, "rb") as f:
                lines = f.readlines()

            filesize = os.path.getsize(filename)
        except IOError as err:
            print(("Error loading hex file: %s" % err))
            return

        print(("filesize: %d bytes of max %d bytes" % (filesize, MAX_SIZE)));
        if filesize >= MAX_SIZE:
            print("hex file too large. Can't upload.");
            return

        for i in range(16):
            if not ch.ser.write(bytearray((0x45,))):
                print("Cannot write programming header.")
                return
        sleep(.1)

        if not ch.ser.write(bytearray(struct.pack("<H", filesize))):
            print("Cannot write hex file size header.")
            return

        sleep(.1)

        for i, line in enumerate(lines): 
            if not line:
                break

            if not ch.ser.write(bytearray(line)):
                print("Cannot write to device.")
                return

            print(("%03d/%03d\b\b\b\b\b\b\b\b" % (i, len(lines))), end=' ')
            sys.stdout.flush()
            sleep(.05)

        print("Write complete.")
        
if __name__ == '__main__':
    send_firmware()
