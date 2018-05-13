#!/usr/bin/python

import os
import sys
import math
import serial
from subprocess import check_call, CalledProcessError
import struct
import function
import random
import common
from color import Color
from time import sleep, time

BAUD_RATE = 38400
NUM_PIXELS = 4
NUM_NODES = 30 
MAX_NODES = 120 
MAX_CLASSES = 16
MAX_PACKET_LEN = 230
CALIBRATION_DURATION = 10
NODE_ID_UNKNOWN = 255

PACKET_SINGLE_LED   = 1  
PACKET_SINGLE_COLOR = 2  
PACKET_COLOR_ARRAY  = 3  
PACKET_PATTERN      = 4  
PACKET_ENTROPY      = 5  
PACKET_START        = 6  
PACKET_CLEAR        = 7  
PACKET_STOP         = 8  
PACKET_POSITION     = 9  
PACKET_DELAY        = 10 
PACKET_ADDRR        = 11 
PACKET_SPEED        = 12 
PACKET_CLASSES      = 13 
PACKET_CALIBRATE    = 14
PACKET_BRIGHTNESS   = 15
PACKET_ANGLE        = 16
PACKET_BOOTLOADER   = 17
PACKET_RESET        = 18
BROADCAST = 0

# Can't find a good constant for ALT0 in GPIO
ALT0 = 4

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



class HippieTrap(object):

    def __init__(self, device = "/dev/serial0"):
        self.ser = None
        self.device = device


    def __enter__(self):

        try:
            check_call(["gpio", "-g", "mode", "14", "alt5"])
        except CalledProcessError as err:
            print "Is wiringpi installed? error: ", err
            sys.exit(-1)

        try:
            self.ser = serial.Serial(self.device, 
                                     BAUD_RATE, 
                                     bytesize=serial.EIGHTBITS, 
                                     parity=serial.PARITY_NONE, 
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=.01)
        except serial.serialutil.SerialException, e:
            print "Cant open serial port: %s" % self.device
            sys.exit(-1)

        # Wait for things to settle, then pipe some characters through the line to get things going
        sleep(.250)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        # sleep just a moment to let the bottles process whatever packet might've
        # been transmitting if we got interrupted
        sleep(.1)
        if self.ser:
            self.ser.close()

        try:
            check_call(["gpio", "-g", "mode", "14", "output"])
        except CalledProcessError as err:
            print "Is wiringpi installed? error: ", err
            sys.exit(-1)

    def send_panic(self):
        while True:
            self.ser.write('M')
            sleep(.0005)

    def clear_cruft(self):
        for i in range(32):
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
        packet = struct.pack("<BBB", 0xBE, 0xEF, len(packet) + 2) + packet + struct.pack("<H", crc)
        if len(packet) > MAX_PACKET_LEN:
            raise BufferError("Max packet len of %d exceeded. Make your pattern smaller." % MAX_PACKET_LEN)
        for ch in packet:
            self.ser.write(chr(ch))
#            print "%02X " % ch,
#        print

    def send_entropy(self):
        for dest in xrange(1, NUM_NODES + 1):
            self._send_packet(dest, PACKET_ENTROPY, bytearray(os.urandom(4)))

    def set_color(self, dest, col):
        self._send_packet(dest, PACKET_SINGLE_COLOR, bytearray((col[0], col[1], col[2])))

    def set_single_led(self, dest, led, col):
        self._send_packet(dest, PACKET_SINGLE_LED, bytearray((led, col[0], col[1], col[2])))

    def set_color_array(self, dest, colors):
        packet = bytearray()
        for col in colors:
            packet += bytearray((col[0], col[1], col[2]))
        self._send_packet(dest, PACKET_COLOR_ARRAY, packet)

    def send_pattern(self, dest, id):
        self._send_packet(dest, PACKET_PATTERN, bytearray(bytes((chr(id)))))

        # Give the bottles a moment to parse the packet before we go on
        sleep(.05)

    def send_fade(self, dest, steps, colors):
        packet = bytearray(struct.pack("<BH", 0, steps))
        for col in colors:
            packet += bytearray((col[0], col[1], col[2]))
        self._send_packet(dest, PACKET_PATTERN, packet)

    def send_rainbow(self, dest, divisor):
        packet = bytearray(struct.pack("<BB", 1, divisor))
        self._send_packet(dest, PACKET_PATTERN, packet)

    def send_decay(self, dest, divisor):
        packet = bytearray(struct.pack("<BB", 2, divisor))
        self._send_packet(dest, PACKET_PATTERN, packet)

    def start_pattern(self, dest):
        self._send_packet(dest, PACKET_START, bytearray())

    def stop_pattern(self, dest):
        self._send_packet(dest, PACKET_STOP, bytearray())

    def send_invalid_packet(self, id):
        self._send_packet(BROADCAST, 254, bytearray()) 

    def clear(self, dest):
        self._send_packet(dest, PACKET_CLEAR, bytearray()) 

    def fade_out(self, dest):
        self.stop_pattern(dest) 
        self.send_decay(dest, 10);
        self.start_pattern(dest) 
        sleep(.5)
        self.clear(dest)

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

    def enter_bootloader(self, dest):
        self._send_packet(dest, PACKET_BOOTLOADER, bytearray()) 

    def reset_nodes(self, dest):
        self._send_packet(dest, PACKET_RESET, bytearray()) 

    def set_brightness(self, dest, brightness):
        self._send_packet(dest, PACKET_BRIGHTNESS, bytearray(struct.pack("<B", brightness))) 

    def set_classes(self, classes):
        if not isinstance(classes, list):
            raise TypeError("Second argument to set_classes must be a list of lists")
        if len(classes) > MAX_CLASSES:
            raise ValueError("Too many classes defined. Max %d allowed." % MAX_CLASSES)

        nodes = [ [] for i in xrange(NUM_NODES+1) ]
        for i, cls in enumerate(classes):
            for node in cls:
                nodes[node].append(i) 

        for i, classes_per_node in enumerate(nodes):
            if classes_per_node:
                self._send_packet(i, PACKET_CLASSES, bytearray(classes_per_node))

    def calibrate_timers(self, dest):
        self._send_packet(dest, PACKET_CALIBRATE, bytearray((CALIBRATION_DURATION,))) 
        sleep(1)
        print "Start calibration..."
        self.ser.write(chr(1));
        sleep(CALIBRATION_DURATION);
        self.ser.write(chr(0));
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
