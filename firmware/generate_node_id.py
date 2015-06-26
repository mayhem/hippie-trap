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

PUMP_ID_FILE = "last_node_id.txt"

def get_random_node_id():
    random.seed()
    return random.randint(0, 254)

def get_node_id():

    # Get a random id, just in case.
    id = get_random_node_id()
    id_file = None

    # now try and see if we've got a saved node id. If so, increment by one and save it
    try:
        id_file = open(PUMP_ID_FILE, "r")
        id = int(id_file.readline().strip()) + 1

        # Roll over the id, avoiding 255 and 0
        if id == 255:
            id = 1
    except IOError:
        pass
    except ValueError:
        print "Warning: Cannot read saved node id. Try removing file %s " % PUMP_ID_FILE

    if id_file:
        id_file.close()

    try:
        id_file = open(PUMP_ID_FILE, "w")
        id_file.write(chr(id))
    except IOError:
        print "Failed to save node id to %s" % PUMP_ID_FILE

    if id_file:
        id_file.close()

    return id

parser = argparse.ArgumentParser()
parser.add_argument("file", help="The filename to write the node id to")
parser.add_argument("id", nargs='?', help="The node id to write to the file.", type=int, default=-1)
args = parser.parse_args()

if args.id < 0:
    id = get_node_id()
else:
    id = args.id

try:
    f = open(args.file, "a")
    f.write(struct.pack("B", id))
    f.close()
except IOError, e:
    print "Error: ", e
    sys.exit(-1)

print "Pump id %x written to %s" % (id, sys.argv[1])
sys.exit(0)
