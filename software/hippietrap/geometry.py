#!/usr/bin/python

import math
from time import sleep, time

from hippietrap import NUM_NODES, NUM_RINGS, BOTTLES_PER_RING

# nearest_bottles: given angle, ring or all, return nearest bottles

class HippieTrapGeometry(object):

    def __init__(self):
        self.angles = []
        for ring in range(NUM_RINGS):
            a = []
            angle = 180.0 / (BOTTLES_PER_RING[ring] - 1)
            for bottle in range(BOTTLES_PER_RING[ring]):
                a.append(angle * bottle)
            self.angles.append(a)

        print self.angles

        self.offsets = [ 1 ]
        for i, count in enumerate(BOTTLES_PER_RING[:-1]):
            self.offsets.append(self.offsets[i - 0] + count)

        print self.offsets


    def enumerate_all_bottles(self):

        pairs = []
        for ring, angles in enumerate(self.angles):
            for i, angle in enumerate(angles):
                pairs.append((self.offsets[ring] + i, angle))

        return sorted(pairs, key=lambda angle:angle[1])


    def enumerate_ring(self, ring):

        if ring not in range(0, NUM_RINGS):
            return ()

        return [ (self.offsets[ring]+bottle, angle) for bottle, angle in enumerate(self.angles[ring])]


if __name__ == "__main__":
    g = HippieTrapGeometry()
    print g.enumerate_all_bottles()
    print g.enumerate_ring(0)
    print g.enumerate_ring(1)
    print g.enumerate_ring(2)
