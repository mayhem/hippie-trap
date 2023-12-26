#!/usr/bin/env python3

import os
import sys
from time import sleep
from hippietrap import HippieTrap, ALL, NUM_NODES
from hippietrap.pattern import PatternBase, run_pattern

# TODO: Add sparkle.
# TODO: Consider color pallete mapping. Map a sub-range to the whole.
# TODO: Add dimming plugin that adds dimming shimmer effects. Could be coordinated for
#       a grid effect on a circlar medium.


class EachBottleOneRainbowPattern(PatternBase):

    name = "each bottle one rainbow"

    def pattern(self):

        self.trap.send_entropy()
        for i in range(NUM_NODES):
            self.trap.send_rainbow(i + 1, 4)
            self.trap.start_pattern(i + 1)
            sleep(.01)

        while not self.stop_thread:
            sleep(.1)

        self.trap.stop_pattern(ALL)


if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        trap.set_brightness(ALL, 100)

        p = EachBottleOneRainbowPattern(trap)
        p.pattern()
