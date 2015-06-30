#!/usr/bin/env python

# Original code Copyright (c) Party Robotics 2014
# Released under GPL v2
# https://github.com/partyrobotics/bartendro/blob/master/firmware/dispenser/pump_id.py

import sys
import struct
import subprocess
import random
import argparse
import errno

NODE_ID_FILE = "/tmp/node.raw"
FUSE_CALL = ["sudo", "avrdude", "-u", "-p", "m328p", "-P", "usb", "-c", "avrispmkII", "-U", "lfuse:w:0xe2:m", "-U", "hfuse:w:0xd1:m", "-U", "efuse:w:0xff:m"]
ID_CALL = ["sudo", "avrdude", "-p", "m328p", "-P", "usb", "-c", "avrispmkII", "-U", "eeprom:w:" + NODE_ID_FILE + ":r"]
PROGRAM_CALL = ["sudo", "avrdude", "-p", "m328p", "-P", "usb", "-c", "avrispmkII", "-Uflash:w:"]

def write_node_id(file_name, id):
    try:
        id_file = open(file_name, "w")
        id_file.write(struct.pack("B", id))
    except IOError:
        print "Failed to save node id to %s" % file_name
        sys.exit(-1)

    id_file.close()

parser = argparse.ArgumentParser()
parser.add_argument("id", help="The next node id to use", type=int, default=1)
parser.add_argument("hex", help="The hex file to program", default=None)
args = parser.parse_args()

id = args.id
hex = args.hex

PROGRAM_CALL[-1] += hex

while True:
    print "programming fuses: *******************************"
    try:
        subprocess.check_call(FUSE_CALL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        pass

    print "writing node id: *********************************"
    write_node_id(NODE_ID_FILE, id)
    try:
        subprocess.check_output(ID_CALL)
    except subprocess.CalledProcessError as e:
        pass

    print "writing hex file: *********************************"
    try:
        subprocess.check_output(PROGRAM_CALL)
    except subprocess.CalledProcessError as e:
        pass

    print "Node %d programmed. Press key for next node." % id
    raw_input("")
    id += 1
