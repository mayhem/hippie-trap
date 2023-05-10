#!/usr/bin/python

import os
import sys
import math
import serial
from subprocess import check_call, CalledProcessError
import struct
from . import function
import random
from . import common
from .color import Color
from time import sleep, time

BAUD_RATE = 38400
NUM_PIXELS = 4
NUM_NODES = 72 
MAX_NODES = 101 
MAX_GROUPS = 16
NUM_RINGS = 4 
BOTTLES_PER_RING = (13, 17, 19, 23) #, 29)
RING_RADII = [54, 84, 115, 144] # in cm

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
PACKET_GROUPS       = 13 
PACKET_CALIBRATE    = 14
PACKET_BRIGHTNESS   = 15
PACKET_ANGLE        = 16
PACKET_BOOTLOADER   = 17
PACKET_RESET        = 18
PACKET_RANDOM_COLOR = 19

# Broadcast IDs
BROADCAST = 0
ALL = BROADCAST           # is shorter!

# Can't find a good constant for ALT0 in GPIO
ALT0 = 4

POWER_GPIO_PINS = [ 35, 37, 38, 40 ]

def crc16_update(crc, a):
    crc ^= a
    for i in range(0, 8):
        if crc & 1:
            crc = (crc >> 1) ^ 0xA001
        else:
            crc = (crc >> 1)
    return crc

def group(grp):
    if grp >= MAX_GROUPS:
        raise ValueError("Invalid group id %d. Max group id is %d." % (grp, MAX_GROUPS))
    return grp | 0x80


class HippieTrap(object):

    def __init__(self, device = "/dev/serial0"):
        self.ser = None
        self.device = device
        self.brightness = 100


    def __enter__(self):

        try:
            check_call(["gpio", "-g", "mode", "14", "alt5"])

            for pin in POWER_GPIO_PINS:
                check_call(["gpio", "-1", "mode", "%d" % pin, "output"])

        except CalledProcessError as err:
            print("Is wiringpi installed? error: ", err)
            sys.exit(-1)

        try:
            self.ser = serial.Serial(self.device, 
                                     BAUD_RATE, 
                                     bytesize=serial.EIGHTBITS, 
                                     parity=serial.PARITY_NONE, 
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=.01,
                                     exclusive=True)
        except serial.serialutil.SerialException as e:
            print("Cant open serial port: %s" % self.device)
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
            print("Is wiringpi installed? error: ", err)
            sys.exit(-1)

    def send_panic(self):
        while True:
            self.ser.write(bytearray((ord('M'),)))
            sleep(.0005)


    def begin(self):

        self.set_brightness(BROADCAST, 100)
        self.stop_pattern(BROADCAST)
        self.clear(BROADCAST)
        sleep(.1)


    def power_on(self):

        if not self.ser or not self.ser.is_open:
            raise IOError("Hippie trap not opened.")

        try:
            for pin in POWER_GPIO_PINS:
                check_call(["gpio", "-1", "write", "%d" % pin, "1"])
                sleep(.25)

        except CalledProcessError as err:
            print("Is wiringpi installed? error: ", err)
            sys.exit(-1)

        print("wait 2 seconds for bottle startup")
        sleep(2)
        print("done")


    def power_off(self):
        if not self.ser or not self.ser.is_open:
            raise IOError("Hippie trap not opened.")

        try:
            for pin in POWER_GPIO_PINS:
                check_call(["gpio", "-1", "write", "%d" % pin, "0"])

        except CalledProcessError as err:
            print("Is wiringpi installed? error: ", err)
            sys.exit(-1)

        print("done")


    def clear_cruft(self):
        for i in range(32):
            self.ser.write(bytearray((chr(0),)))


    def dump(self, msg, p):
        print("%s " % msg, end='')
        for ch in p:
            print("%02X " % ch, end=''),
        print("")


    def _send_packet(self, dest, type, data):
        if not self.ser:
            return

        if not isinstance(data, bytearray):
            print("data argument to send_packet must be bytearray")
            return

        packet = bytearray(struct.pack("<BB", dest, type)) + data
        crc = 0
        for ch in packet:
            crc = crc16_update(crc, ch)
        packet = bytearray(struct.pack("<BBB", 0xBE, 0xEF, len(packet) + 2)) + packet + struct.pack("<H", crc)
        if len(packet) > MAX_PACKET_LEN:
            raise BufferError("Max packet len of %d exceeded. Make your pattern smaller." % MAX_PACKET_LEN)
        for ch in packet:
            self.ser.write(bytearray((ch,)))

    def send_entropy(self):
        for dest in range(1, NUM_NODES + 1):
            self._send_packet(dest, PACKET_ENTROPY, bytearray(os.urandom(4)))

    def set_color(self, dest, col):
        self._send_packet(dest, PACKET_SINGLE_COLOR, bytearray(struct.pack("<BBB", col[0], col[1], col[2])))

    def set_single_led(self, dest, led, col):
        self._send_packet(dest, PACKET_SINGLE_LED, struct.pack("<BBB", col[0], col[1], col[2]))

    def set_random_color(self, dest):
        self._send_packet(dest, PACKET_RANDOM_COLOR, bytearray()) 

    def set_color_array(self, dest, colors):
        packet = bytearray()
        for col in colors:
            packet += struct.pack("<BBB", col[0], col[1], col[2])
        self._send_packet(dest, PACKET_COLOR_ARRAY, packet)

    def send_pattern(self, dest, id):
        self._send_packet(dest, PACKET_PATTERN, bytearray(bytes((chr(id)))))

        # Give the bottles a moment to parse the packet before we go on
        sleep(.05)

    def send_fade(self, dest, steps, colors, hue_shift=0):
        packet = bytearray(struct.pack("<BHB", 0, steps, hue_shift))
        for col in colors:
            packet += bytearray((col[0], col[1], col[2]))
        self._send_packet(dest, PACKET_PATTERN, packet)

    def send_rainbow(self, dest, divisor):
        packet = bytearray(struct.pack("<BB", 1, divisor))
        self._send_packet(dest, PACKET_PATTERN, packet)

    def send_decay(self, dest, divisor):
        packet = bytearray(struct.pack("<BB", 2, divisor))
        self._send_packet(dest, PACKET_PATTERN, packet)

    def send_sin(self, dest, period, phase, amplitude, offset):
        packet = bytearray(struct.pack("<Bllll", 3, period, phase, amplitude, offset))
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
        if self.brightness != brightness:
            self.brightness = brightness
            self._send_packet(dest, PACKET_BRIGHTNESS, bytearray(struct.pack("<B", brightness))) 

    def increase_brightness(self, dest):
        if self.brightness < 10:
            brightness = 10
        else:
            brightness = min(self.brightness + 10, 100)
        self.set_brightness(dest, brightness)

    def decrease_brightness(self, dest):
        self.set_brightness(dest, max(self.brightness - 10, 5))

    def set_groups(self, groups):
        if not isinstance(groups, list) and not isinstance(groups, tuple):
            raise TypeError("Second argument to set_groups must be a list/tuple of lists/tuples")
        if len(groups) > MAX_GROUPS:
            raise ValueError("Too many groups defined. Max %d allowed." % MAX_GROUPS)

        nodes = [ [] for i in range(NUM_NODES+1) ]
        for i, grp in enumerate(groups):
            for node in grp:
                nodes[node].append(i) 

        for i, groups_per_node in enumerate(nodes):
            if groups_per_node:
                self._send_packet(i, PACKET_GROUPS, bytearray(groups_per_node))

    def calibrate_timers(self, dest):
        self._send_packet(dest, PACKET_CALIBRATE, bytearray((CALIBRATION_DURATION,))) 
        sleep(1)
        print("Start calibration...")
        self.ser.write(bytearray(bytes(chr(1), encoding="ascii")))
        sleep(CALIBRATION_DURATION);
        self.ser.write(bytearray(bytes(chr(0), encoding="ascii")))
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
