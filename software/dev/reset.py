#!/usr/bin/python

import os
import sys
import math
from hippietrap.hippietrap import HippieTrap, BROADCAST

with HippieTrap() as ch:
    ch.reset_nodes(BROADCAST)
