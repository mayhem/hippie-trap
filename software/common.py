#!/usr/bin/python

import abc

class Color(object):

    def __init__(self, r, g, b):
        self.color = [r, g, b]

    def __str__(self):
        return "Color(%d,%d,%d)" % (self.color[0], self.color[1], self.color[2])

    @abc.abstractmethod
    def __getitem__(self, i):
        return self.color[i]

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

