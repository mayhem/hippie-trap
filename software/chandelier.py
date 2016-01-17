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
import common
from color import Color
from time import sleep, time

BAUD_RATE = 38400
NUM_PIXELS = 4
NUM_NODES = 24
MAX_NODES = 120 
MAX_CLASSES = 16
MAX_PACKET_LEN = 230
CALIBRATION_DURATION = 10
NODE_ID_UNKNOWN = 255

PACKET_SET_ID       = 0 
PACKET_CLEAR_ID     = 1  
PACKET_SINGLE_COLOR = 2  
PACKET_COLOR_ARRAY  = 3  
PACKET_PATTERN      = 4  
PACKET_ENTROPY      = 5  
PACKET_NEXT         = 6  
PACKET_OFF          = 7  
PACKET_CLEAR_NEXT   = 8  
PACKET_POSITION     = 9  
PACKET_DELAY        = 10 
PACKET_ADDRR        = 11 
PACKET_SPEED        = 12 
PACKET_CLASSES      = 13 
PACKET_CALIBRATE    = 14
PACKET_BRIGHTNESS   = 15
PACKET_ANGLE        = 16
BROADCAST = 0

def crc16_update(crc, a):
    crc ^= a
    for i in xrange(0, 8):
        if crc & 1:
            crc = (crc >> 1) ^ 0xA001
        else:
            crc = (crc >> 1)
    return crc

def mkcls(cls):
    if cls >= MAX_CLASSES:
        raise ValueError("Invalid class id %d. Max class id is %d." % (cls, MAX_CLASSES))
    return cls + MAX_NODES + 1

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

        self.set_speed(BROADCAST, 1000)

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
        if len(packet) > MAX_PACKET_LEN:
            raise BufferError("Max packet len of %d exceeded. Make your pattern smaller." % MAX_PACKET_LEN)
        self.ser.write(packet)

    def send_entropy(self):
        for dest in xrange(1, NUM_NODES + 1):
            self._send_packet(dest, PACKET_ENTROPY, bytearray(os.urandom(4)))
            sleep(.01)

    def set_color(self, dest, col):
        self._send_packet(dest, PACKET_SINGLE_COLOR, bytearray((col[0], col[1], col[2])))

    def set_color_array(self, dest, colors):
        packet = bytearray()
        for col in colors:
            packet += bytearray(col[0], col[1], col[2])
        self._send_packet(dest, PACKET_COLOR_ARRAY, packet)

    def send_pattern_to_class(self, cls, pattern):
        self._send_packet(mkcls(cls), PACKET_PATTERN, bytearray(pattern.describe()))

        # Give the bottles a moment to parse the packet before we go on
        sleep(.05)

    def send_pattern(self, dest, pattern):
        self._send_packet(dest, PACKET_PATTERN, bytearray(pattern.describe()))

        # Give the bottles a moment to parse the packet before we go on
        sleep(.05)

    def set_id(self, id):
        self._send_packet(BROADCAST, PACKET_SET_ID, bytearray(struct.pack("<b", id))) 

    def clear_ids(self):
        self._send_packet(BROADCAST, PACKET_CLEAR_ID, bytearray()) 

    def next_pattern(self, dest, transition_steps):
        self._send_packet(dest, PACKET_NEXT, bytearray(struct.pack("<H", transition_steps))) 

    def off(self, dest):
        self._send_packet(dest, PACKET_OFF, bytearray()) 

    def set_delay(self, dest, delay):
        self._send_packet(dest, PACKET_DELAY, bytearray(struct.pack("<b", delay))) 

    def set_speed(self, dest, speed):
        self._send_packet(dest, PACKET_SPEED, bytearray(struct.pack("<H", speed))) 

    def set_position(self, dest, x, y, z):
        x = int(x * common.SCALE_FACTOR)
        y = int(y * common.SCALE_FACTOR)
        z = int(z * common.SCALE_FACTOR)
        self._send_packet(dest, PACKET_POSITION, bytearray(struct.pack("<hhh", x, y, z))) 

    def set_angle(self, dest, a):
        a = int(a * common.SCALE_FACTOR)
        self._send_packet(dest, PACKET_ANGLE, bytearray(struct.pack("<I", a))) 

    def set_brightness(self, dest, brightness):
        self._send_packet(dest, PACKET_BRIGHTNESS, bytearray((brightness,)))

    def clear_next_pattern(self, dest):
        self._send_packet(dest, PACKET_CLEAR_NEXT, bytearray()) 

    def set_classes(self, classes):
        if not isinstance(classes, list):
            raise TypeError("Second argument to set_classes must be a list of lists")
        if len(classes) > MAX_CLASSES:
            raise ValueError("Too many classes defined. Max %d allowed." % MAX_CLASSES)

        nodes = [ [] for i in xrange(NUM_NODES) ]
        for i, cls in enumerate(classes):
            for node in cls:
                nodes[node].append(i) 

        for i, classes_per_node in enumerate(nodes):
            if classes_per_node:
                self._send_packet(i, PACKET_CLASSES, bytearray(classes_per_node))

    def calibrate_timers(self, dest):
        self._send_packet(dest, PACKET_CALIBRATE, bytearray((CALIBRATION_DURATION,))) 
        sleep(1)
        print "start calibration"
        self.ser.write(chr(1));
        sleep(CALIBRATION_DURATION);
        self.ser.write(chr(0));
        print "calibration complete"
        sleep(1)
        self.set_color(BROADCAST, (0,0,0))

    def debug_serial(self, duration = 0):
        finish = duration + time()
        while duration == 0 or time() < finish:
            if self.ser.inWaiting() > 0:
                ch = self.ser.read(1)
                sys.stdout.write(ch);
                sys.stdout.flush()

    def run(self, function, delay, duration = 0.0):
        start_t = time()
        while True:
            t = time() - start_t
            col = function[t]
            #print "%2.3f - %3d,%3d,%3d" % (t, col[0], col[1], col[2])
            self.set_color(BROADCAST, col)
            self.debug_serial(delay)

            if duration > 0 and t > duration:
                break

        # clean up local variables
        generator.clear_local_random_values()
