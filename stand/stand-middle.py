#!/usr/bin/env python

from math import pi, sin, cos, radians
import svgwrite

plate_dia = 270
pole_dia = 13
hole_dia = 17

origin_x = plate_dia + 50
origin_y = plate_dia + 50

circle_spacing = 38

# ---

plate_r = plate_dia / 2.0
pole_r = pole_dia / 2.0
hole_r = hole_dia / 2.0

def border(dwg, radius, origin_x, origin_y):
    STEPS = 360
    points = []
    for i in range(STEPS):
        theta = i * (pi * 2.0) / STEPS
        r1 = radius + (11 * sin(11 * radians(i) + 1.65)) + (7 * sin(5 * radians(i) + 1.65))
        y1 = r1 * sin(theta) + origin_y
        x1 = r1 * cos(theta) + origin_x
        points.append((x1, y1))

    dwg.add(dwg.polygon(points, fill='none', stroke=svgwrite.rgb(0, 0, 0, '%')))

def pocket(dwg, x, y):
    dwg.add(dwg.circle((x, y), hole_r, stroke=svgwrite.rgb(0, 0, 0, '%')))

def pocket_circle(dwg, radius, count, x_off, y_off, jitter):
    for i in range(count):
        theta = i * (pi * 2.0) / count
        y = radius * sin(theta) 
        x = radius * cos(theta)
        pocket(dwg, x + x_off, y + y_off)

dwg = svgwrite.Drawing('middle.svg', profile='tiny')

border(dwg, plate_r, origin_x, origin_y)
pocket(dwg, origin_x, origin_y)

for i, args in enumerate(((5, 0), (7, 0), (11, 5))):
    pocket_circle(dwg, (i + 1) * circle_spacing, args[0], origin_x, origin_y, args[1])

dwg.save()
