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

        self.offsets = [ 1 ]
        for i, count in enumerate(BOTTLES_PER_RING[:-1]):
            self.offsets.append(self.offsets[i - 0] + count)


    def enumerate_all_bottles(self, reverse=False):

        pairs = []
        for ring, angles in enumerate(self.angles):
            for i, angle in enumerate(angles):
                pairs.append((self.offsets[ring] + i, angle))

        bottles = sorted(pairs, key=lambda angle:angle[1])
        if reverse:
            bottles.reverse()

        return bottles


    def enumerate_ring(self, ring, reverse=False):

        if ring not in range(0, NUM_RINGS):
            return ()

        bottles = [ (self.offsets[ring]+bottle, angle) for bottle, angle in enumerate(self.angles[ring])]
        if reverse:
            bottles.reverse()

        return bottles

    def get_ring_from_bottle(self, bottle):

        for ring in range(NUM_RINGS):
            if bottle < self.offsets[ring] + BOTTLES_PER_RING[ring]:
                return ring

    def get_near_bottles(self, angle, delta):
        bottles = self.enumerate_all_bottles()
        result = []
        for bottle in bottles:
            if math.fabs(angle - bottle[1]) <= delta:
                result.append(bottle)

        return sorted(result, key=lambda angle:angle[1])
        
if __name__ == "__main__":
    g = HippieTrapGeometry()
    print g.enumerate_all_bottles()
    print g.get_near_bottles(90, 15);
