#!/usr/bin/python

import abc

class ChainLink(object):

    def __init__(self):
        self.next = None

    def chain(self, next):
        if not self.next:
            self.next = next
        else:
            self.next.chain(next)

    def call_next(self, t, col):
        if self.next:
            return self.next.filter(t, col)
        return col 

