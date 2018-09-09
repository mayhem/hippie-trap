#!/usr/bin/python

import os
import sys
from time import sleep
from hippietrap.hippietrap import HippieTrap, ALL
from hippietrap.pattern import PatternBase, run_pattern


class EachOneRainbow(PatternBase):

    def pattern(self):

        self.trap.send_entropy()
        self.trap.send_rainbow(ALL, 4)
        self.trap.start_pattern(ALL)

        while not self.stop_thread:
            sleep(.1)


if __name__ == "__main__":
    with HippieTrap() as trap:
        trap.begin()
        run_pattern(trap, EachOneRainbow)
        trap.clear(ALL)
