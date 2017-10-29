#!/usr/bin/env python3

import sys
import os

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

    with open(filename, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines): 
        if not line:
            break

        for ch in line:
            if not ser.write(ch.encode('ascii')):
                print("Cannot write to device.")
                return
#sleep(.01)

        ser.write(chr(13).encode('ascii'))
        print("wrote line %d of %d" % (i, len(lines)))
        sleep(.1)

    print("Write complete.")
        
if __name__ == '__main__':
    send_firmware()
