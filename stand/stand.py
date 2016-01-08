#!/usr/bin/env python

import math
import svgwrite

plate_dia = 250
pole_dia = 13
hole_dia = 15
conn_dia = 10

circle_spacing = 32

# ---

plate_r = plate_dia / 2.0
pole_r = pole_dia / 2.0
hole_r = hole_dia / 2.0
conn_r = conn_dia / 2.0

def pocket(dwg, x, y):
    # center hole
    dwg.add(dwg.circle((x, y), hole_r, fill='none', stroke=svgwrite.rgb(0, 0, 0, '%')))

    # connector hole
    dwg.add(dwg.circle((x, y), conn_r, stroke=svgwrite.rgb(0, 0, 0, '%')))

def pocket_circle(dwg, radius, count, x_off, y_off):
    for i in range(count):
        theta = i * (math.pi * 2.0) / count
        y = radius * math.sin(theta)
        x = radius * math.cos(theta)
        pocket(dwg, x + x_off, y + y_off)


dwg = svgwrite.Drawing('test.svg', profile='tiny')

# outer circle
dwg.add(dwg.circle((plate_r, plate_r), plate_r, fill='none', stroke=svgwrite.rgb(0, 0, 0, '%')))

pocket(dwg, plate_r, plate_r)

for i, count in enumerate((5, 7, 11)):
    pocket_circle(dwg, (i + 1) * circle_spacing, count, plate_r, plate_r)

dwg.save()
