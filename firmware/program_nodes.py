#!/usr/bin/env python3

# Original code Copyright (c) Party Robotics 2014
# Released under GPL v2
# https://github.com/partyrobotics/bartendro/blob/master/firmware/dispenser/pump_id.py

import sys
import struct
import subprocess
import random
import argparse
import errno
from time import sleep

NODE_ID_FILE = "/tmp/node.raw"
BOOT_CALL = ["make", "-C", "bootloader"]
FUSES_CALL = ["make", "-C", "bootloader", "fuses"]
ID_CALL = ["sudo", "avrdude", "-p", "m328p", "-P", "usb", "-c", "avrispmkII", "-U", "eeprom:w:" + NODE_ID_FILE + ":r"]

def write_node_id(file_name, id):
    try:
        id_file = open(file_name, "wb")
        id_file.write(struct.pack("LLLLB", 0,0,0,0,id)) # 16 bytes of zeros for bootloader + ID
    except IOError:
        print("Failed to save node id to %s" % file_name)
        sys.exit(-1)

    id_file.close()

parser = argparse.ArgumentParser()
parser.add_argument("id", help="The next node id to use", type=int, default=1)
parser.add_argument("delay", help="Delay between progamming nodes", type=int, default=0)
args = parser.parse_args()

id = args.id
delay = args.delay

while True:
    if delay:
        print("Waiting %s seconds..." % delay)
        sleep(delay)
    else:
        print("READY FOR NEXT NODE -- Press key to program")
        raw_input("")

    print("programming bootloader: *******************************")
    try:
        subprocess.check_call(BOOT_CALL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("PROGRAMMING FAILED!!! DO NOT MOVE TO NEXT NODE!")
        continue

    print("programming fuses: *******************************")
    try:
        subprocess.check_call(FUSES_CALL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("PROGRAMMING FAILED!!! DO NOT MOVE TO NEXT NODE!")
        continue

    print("writing node id: *********************************")
    write_node_id(NODE_ID_FILE, id)
    try:
        subprocess.check_output(ID_CALL)
    except subprocess.CalledProcessError as e:
        print("PROGRAMMING FAILED!!! DO NOT MOVE TO NEXT NODE!")
        continue

    print("Node id %d programmed." % id)
    id += 1
