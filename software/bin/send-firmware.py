#!/usr/bin/env python

import sys
import os
import struct
from hippietrap.hippietrap import HippieTrap, BROADCAST

import click
from time import sleep

BAUD_RATE = 38400

@click.command()
@click.argument('filename')
def send_firmware(filename):
    with HippieTrap() as ch:
        try:
            with open(filename, "r") as f:
                lines = f.readlines()

            filesize = os.path.getsize(filename)
        except IOError as err:
            print("Error loading hex file: %s" % err)
            return

        print("filesize: %d (%x) bytes" % (filesize, filesize));
        if filesize >= 0x7000:
            print("hex file too large. Can't upload.");
            return

        for i in range(16):
            if not ch.ser.write(chr(0x45).encode('ascii')):
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

            for char in line:
                if not ch.ser.write(char.encode('ascii')):
                    print("Cannot write to device.")
                    return
                sleep(.0001)

            print("%03d/%03d\b\b\b\b\b\b\b\b" % (i, len(lines))),
            sys.stdout.flush()
            sleep(.05)

        print("Write complete.")
        
if __name__ == '__main__':
    send_firmware()
