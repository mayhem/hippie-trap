#!/usr/bin/python

class Color(object):

    def __init__(self, r, g, b):
        self.color = [r, g, b]

    def __str__(self):
        return "Color(%d,%d,%d)" % (self.color[0], self.color[1], self.color[2])

    @abc.abstractmethod
    def __getitem__(self, i):
        return self.color[i]
