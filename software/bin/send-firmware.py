#!/usr/bin/env python3

import sys
import os
import struct

import click
import serial
from time import sleep

BAUD_RATE = 38400

@click.command()
@click.argument('dev')
@click.argument('filename')
def send_firmware(dev, filename):
    try:
        ser = serial.Serial(dev, 
            BAUD_RATE, 
            bytesize=serial.EIGHTBITS, 
            parity=serial.PARITY_NONE, 
            stopbits=serial.STOPBITS_ONE,
            timeout=.01)
    except serial.serialutil.SerialException as e:
        print("Cannot open serial port: %s" % port)
        return 

    try:
        with open(filename, "r") as f:
            lines = f.readlines()

        filesize = os.path.getsize(filename)
    except IOError as err:
        print("Error loading hex file: %s" % err)
        return

    for i in range(16):
        if not ser.write(chr(0x45).encode('ascii')):
            print("Cannot write programming header.")
            return
    sleep(.1)

    print("filesize: %d bytes" % filesize);
    if not ser.write(bytearray(struct.pack("<H", filesize))):
        print("Cannot write hex file size header.")
        return

    sleep(.1)

    for i, line in enumerate(lines): 
        if not line:
            break

        for ch in line:
            if not ser.write(ch.encode('ascii')):
                print("Cannot write to device.")
                return

        ser.write(chr(13).encode('ascii'))
        print("wrote line %d of %d" % (i, len(lines)))
        sleep(.015)

    print("Write complete.")
        
if __name__ == '__main__':
    send_firmware()
