#!/usr/bin/python

import math
import serial
import struct
import function
import generator
import filter
from time import sleep, time
from color import Color, RandomColorSequence

BAUD_RATE = 38400

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

    def set_color(self, red, green, blue):
        packet = chr(red) + chr(green) + chr(blue);
        crc = 0
        for ch in packet:
            crc = crc16_update(crc, ord(ch))
        packet = struct.pack("<BB", 255,  len(packet) + 2) + packet + struct.pack("<H", crc)
        self.ser.write(packet)

# TODO:     packet = chr(red) + chr(green) + chr(blue);
#    ValueError: chr() arg not in range(256)

    def run(self, function, delay, duration = 0.0):
        start_t = time()
        while True:
            t = time() - start_t
            col = function[t]
            ch.set_color(col[0], col[1], col[2])
            sleep(delay)

            if duration > 0 and t > duration:
                break

DELAY = .02

ch = Chandelier()
ch.open("/dev/ttyAMA0")

#rainbow = function.Rainbow(.05)
#rainbow.chain(filter.FadeIn(2))
#purple = function.ConstantColor(Color(128, 0, 128))
#purple.chain(filter.FadeIn(2.0))
#purple.chain(filter.FadeOut(4.0, 2.0))

rand_col = RandomColorSequence()
while True:
    wobble = function.ConstantColor(rand_col.get())
    period_s = 1
    g = generator.Sin((math.pi * 2) / period_s, -math.pi/2, .5, .5)
    wobble.chain(filter.Brightness(g))
    ch.run(wobble, DELAY, period_s)
