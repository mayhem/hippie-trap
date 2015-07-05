#!/usr/bin/python

import os
import sys
import serial
import urllib2
from time import sleep, time

BAUD_RATE = 9600
#IP = "127.0.0.1"
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

            arg =""
            if ch == "0":
                arg = "skip"
            elif ch == "1":
                arg = "bdown"
            elif ch == "2":
                arg = "sdown"
            elif ch == "3":
                arg = "bup"
            elif ch == "4":
                arg = "hold"
            elif ch == "5":
                arg = "sup"

            if arg:
                print arg
                url = "http://%s:%d/ctrl/%s" % (IP, PORT, arg)
                try:
                    urllib2.urlopen(url)
                except urllib2.URLError:
                    pass
                except urllib2.HTTPError:
                    pass

if __name__ == "__main__":
    r = Relay()
    r.open("/dev/ttyAMA0")
    r.run()
