#!/usr/bin/python

import sys
import math
import serial
import struct
import function
import generator
import filter
import random
from time import sleep, time
from color import Color

BAUD_RATE = 38400
NUM_PIXELS = 8

PACKET_SINGLE_COLOR = 0
PACKET_COLOR_ARRAY  = 1
PACKET_PATTERN      = 2
BROADCAST = 0

def crc16_update(crc, a):
    crc ^= a
    for i in xrange(0, 8):
        if crc & 1:
            crc = (crc >> 1) ^ 0xA001
        else:
            crc = (crc >> 1)
    return crc

class Chandelier(object):

    def __init__(self):
        self.ser = None

    def open(self, device):

        try:
            print "Opening %s" % device
            self.ser = serial.Serial(device, 
                                     BAUD_RATE, 
                                     bytesize=serial.EIGHTBITS, 
                                     parity=serial.PARITY_NONE, 
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=.01)
        except serial.serialutil.SerialException, e:
            print "Cant open serial port: %s" % device
            sys.exit(-1)

        # Wait for things to settle, then pipe some characters through the line to get things going
        sleep(.250)
        self.ser.write(chr(0))
        self.ser.write(chr(0))
        self.ser.write(chr(0))

    def set_color(self, dest, col):
        packet = chr(dest) + chr(PACKET_SINGLE_COLOR) + chr(col[0]) + chr(col[1]) + chr(col[2])
        crc = 0
        for ch in packet:
            crc = crc16_update(crc, ord(ch))
        packet = struct.pack("<BB", 255,  len(packet) + 2) + packet + struct.pack("<H", crc)
        self.ser.write(packet)

    def set_color_array(self, dest, colors):
        packet = chr(dest) + chr(PACKET_COLOR_ARRAY)
        for col in colors:
            packet += chr(col[0]) + chr(col[1]) + chr(col[2]);
        crc = 0
        for ch in packet:
            crc = crc16_update(crc, ord(ch))
        packet = struct.pack("<BB", 255,  len(packet) + 2) + packet + struct.pack("<H", crc)
        self.ser.write(packet)

    def send_pattern(self, dest, pattern):
        packet = chr(dest) + chr(PACKET_PATTERN) + pattern.describe() 
        crc = 0
        for ch in packet:
            crc = crc16_update(crc, ch)
        packet = struct.pack("<BB", 255,  len(packet) + 2) + packet + struct.pack("<H", crc)
        self.ser.write(packet)

    def print_debug(self):
        while True:
            ch = self.ser.read(1)
            if ch:
                sys.stdout.write(ch);
                sys.stdout.flush()

    def run(self, function, delay, duration = 0.0):
        start_t = time()
        while True:
            t = time() - start_t
            col = function[t]
            array = []
            for i in xrange(NUM_PIXELS):
                array.append(col)

            ch.set_color_array(BROADCAST, array)
            sleep(delay)

            if duration > 0 and t > duration:
                break

DELAY = .02

device = "/dev/ttyAMA0"
if len(sys.argv) == 2:
    device = sys.argv[1]

ch = Chandelier()
ch.open(device)

random.seed()
period_s = 1

rainbow = function.Rainbow(generator.Sawtooth(.55))
rainbow.chain(filter.FadeIn(1))
rainbow.chain(filter.FadeOut(1.0, 5.0))

purple = function.ConstantColor(Color(128, 0, 128))
purple.chain(filter.FadeIn(1.0))
purple.chain(filter.FadeOut(1.0, 5.0))

wobble = function.RandomColorSequence(period_s, random.randint(0, 255))
g = generator.Sin((math.pi * 2) / period_s, -math.pi/2, .5, .5)
wobble.chain(filter.Brightness(g))

#funcs = [rainbow, wobble]
#while True:
#    wobble = function.RandomColorSequence(period_s, random.randint(0, 255))
#    g = generator.Sin((math.pi * 2) / period_s, -math.pi/2, .5, .5)
#    wobble.chain(filter.Brightness(g))
#    funcs = [wobble]
#    funcs = [purple]

ch.send_pattern(BROADCAST, rainbow)
print "----"
ch.print_debug()
