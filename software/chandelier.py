#!/usr/bin/python

import os
import sys
import math
import serial
import struct
import function
import generator
import filter
import random
from color import Color
from time import sleep, time

BAUD_RATE = 38400
NUM_PIXELS = 4
NUM_NODES = 101

PACKET_SINGLE_COLOR = 0
PACKET_COLOR_ARRAY  = 1
PACKET_PATTERN      = 2
PACKET_ENTROPY      = 3
PACKET_NEXT         = 4
PACKET_OFF          = 5
PACKET_CLEAR_NEXT   = 6
PACKET_POSITION     = 7
PACKET_DELAY        = 8
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

    def _send_packet(self, dest, type, data):
        if not self.ser:
            return

        if not isinstance(data, bytearray):
            print "data argument to send_packet must be bytearray"
            return

        packet = chr(dest) + chr(type) + data
        crc = 0
        for ch in packet:
            crc = crc16_update(crc, ch)
        packet = struct.pack("<BB", 255,  len(packet) + 2) + packet + struct.pack("<H", crc)
        self.ser.write(packet)

    def send_entropy(self):
        for dest in xrange(NUM_NODES):
            self._send_packet(dest, PACKET_ENTROPY, bytearray(os.urandom(1)))

    def set_color(self, dest, col):
        self._send_packet(dest, PACKET_SINGLE_COLOR, bytearray((col[0], col[1], col[2])))

    def set_color_array(self, dest, colors):
        packet = bytearray()
        for col in colors:
            packet += bytearray(col[0], col[1], col[2])
        self._send_packet(dest, PACKET_COLOR_ARRAY, packet)

    def send_pattern(self, dest, pattern):
        self._send_packet(dest, PACKET_PATTERN, bytearray(pattern.describe())) 

        # Give the bottles a moment to parse the packet before we go on
        sleep(.05)

    def next_pattern(self, dest, transition_steps):
        self._send_packet(dest, PACKET_NEXT, bytearray(struct.pack("<H", transition_steps))) 

    def off(self, dest):
        self._send_packet(dest, PACKET_OFF, bytearray()) 

    def set_delay(self, dest, delay):
        self._send_packet(dest, PACKET_DELAY, bytearray(struct.pack("<b", delay))) 

    def debug_serial(self, duration):
        finish = duration + time()
        while time() < finish:
            if self.ser.inWaiting() > 0:
                ch = self.ser.read(1)
                sys.stdout.write(ch);
                sys.stdout.flush()

    def run(self, function, delay, duration = 0.0):
        start_t = time()
        while True:
            t = time() - start_t
            col = function[t]
            self.set_color(BROADCAST, col)
            self.debug_serial(delay)

            if duration > 0 and t > duration:
                break
