#!/usr/bin/python

import os
import sys
import serial
import socket
from time import sleep, time

BAUD_RATE = 9600
IP = "10.0.0.1"
PORT = 8080

class Relay(object):

    def open(self, device):

        try:
            self.ser = serial.Serial(device, 
                                     BAUD_RATE, 
                                     bytesize=serial.EIGHTBITS, 
                                     parity=serial.PARITY_NONE, 
                                     stopbits=serial.STOPBITS_ONE)
        except serial.serialutil.SerialException, e:
            print "Cant open serial port: %s" % device
            sys.exit(-1)

    def run(self):
        while True:
            ch = self.ser.read(1)
            if not ch:
                continue
            if ch < "0" or ch > "5":
                continue

            if arg:
                try:
                    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM))
                    socket.connect((IP, PORT))
                    socket.send(ch);
                    socket.shutdown(socket.SD_RDWR)
                    socket.close()
                except urllib2.URLError:
                    pass
                except urllib2.HTTPError:
                    pass

if __name__ == "__main__":
    r = Relay()
    r.open("/dev/ttyAMA0")
    r.run()
