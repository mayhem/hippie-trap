#!/usr/bin/python

import os
import sys
from time import sleep
from hippietrap.hippietrap import HippieTrap, ALL
from hippietrap.pattern import PatternBase, run_pattern
from hippietrap.transition import transition_fade_out, transition_drop_out

# TODO: Add sparkle. 
# TODO: Consider color pallete mapping. Map a sub-range to the whole.
# TODO: Add dimming plugin that adds dimming shimmer effects. Could be coordinated for
#       a grid effect on a circlar medium.


class EachBottleOneRainbowPattern(PatternBase):

    name = "each bottle one rainbow"

    def pattern(self):

        self.trap.send_entropy()
        self.trap.send_rainbow(ALL, 4)
        self.trap.start_pattern(ALL)

        while not self.stop_thread:
            sleep(.1)

        self.trap.stop_pattern(ALL)
        if self.transition:
            transition_fade_out(self.trap)
