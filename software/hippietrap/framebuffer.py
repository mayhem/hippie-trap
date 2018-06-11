import os
import sys
import math
from color import Color
from time import sleep, time
from hippietrap import NUM_NODES 


class FrameBuffer(object):

    def __init__(self, trap):
        self._clear()
        self.trap = trap


    def _clear(self):
        self.current_bottles = [ { 'colors' : [ Color(0,0,0) ] * 4, 'dirty' : False } for i in range(30) ]


    def clear(self, mark_dirty = True):
        if not mark_dirty:
            self._clear()
            return

        for i, bottle in enumerate(self.current_bottles):
            for color in bottle['colors']:
                if color != Color(0,0,0):
                    bottle['dirty'] = True
                    bottle['colors'] = [ Color(0,0,0) ] * 4
                    break


    def set_color(self, bottles, colors):
        if isinstance(bottles, int):
            bottles = [ bottles ]

        if isinstance(colors, Color):
            colors = [ colors ] * 4 
        else:
            if type(colors) not in [tuple, list] or len(colors) != 4:
                raise ValueError("Must pass a Color or array of 4 Colors to set_color()")

        for bottle in bottles:
            self.current_bottles[bottle - 1]['colors'] = colors
            self.current_bottles[bottle - 1]['dirty'] = True


    def get_color(self, bottle):
        return self.current_bottles[bottle - 1]['colors']


    def apply(self):

        for i, bottle in enumerate(self.current_bottles):
            if bottle['dirty']:
                self.trap.set_color_array(i + 1, bottle['colors'])                
                bottle['dirty'] = False


if __name__ == "__main__":
    buf = FrameBuffer(None)

    buf.set_color(1, Color(255, 0, 0))
    buf.apply() 
    buf.set_color(2, Color(0, 255, 0))
    buf.apply() 
    buf.set_color(3, Color(0, 0, 255))
    buf.apply() 
    buf.clear()
    buf.apply() 
