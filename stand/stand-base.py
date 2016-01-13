#!/usr/bin/env python

from math import pi, sin, cos, radians
import svgwrite

plate_dia = 270
hole_dia = 15
conn_dia = 10

origin_x = plate_dia + 50
origin_y = plate_dia + 50

circle_spacing = 28

# ---

plate_r = plate_dia / 2.0
hole_r = hole_dia / 2.0
conn_r = conn_dia / 2.0

def border(dwg, radius, origin_x, origin_y):
    STEPS = 360
    points = []
    for i in range(STEPS):
        theta = i * (pi * 2.0) / STEPS
        r1 = radius + (10 * sin(7 * radians(i)))
        y1 = r1 * sin(theta) + origin_y
        x1 = r1 * cos(theta) + origin_x
        points.append((x1, y1))

    dwg.add(dwg.polygon(points, fill='none', stroke=svgwrite.rgb(0, 0, 0, '%')))


def pocket(dwg, x, y):
    # pocket hole
    dwg.add(dwg.circle((x, y), hole_r, fill='rgb(128, 128, 128)'))
    # connector hole
    dwg.add(dwg.circle((x, y), conn_r, fill='rgb(0, 0, 0)'))

def pocket_circle(dwg, radius, count, x_off, y_off):
    for i in range(count):
        theta = i * (pi * 2.0) / count
        y = radius * sin(theta)
        x = radius * cos(theta)
        pocket(dwg, x + x_off, y + y_off)


dwg = svgwrite.Drawing('base.svg', profile='tiny')

border(dwg, plate_r, origin_x, origin_y)
pocket(dwg, origin_x, origin_y)

for i, count in enumerate((5, 7, 11)):
    pocket_circle(dwg, (i + 1) * circle_spacing, count, origin_x, origin_y)

dwg.save()
