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
    for i in range(STEPS - 40):
        theta = i * (pi * 2.0) / STEPS
        r1 = radius + (10 * sin(7 * radians(i)))
        y1 = r1 * sin(theta) + origin_y
        x1 = r1 * cos(theta) + origin_x
        points.append((x1, y1))

    return points


dwg = svgwrite.Drawing('foot.svg', profile='tiny')
points = border(dwg, plate_r, origin_x, origin_y)
inner = border(dwg, plate_r - 36, origin_x, origin_y)
inner.reverse()
points.extend(inner)
dwg.add(dwg.polygon(points, fill='none', stroke=svgwrite.rgb(0, 0, 0, '%')))
dwg.save()
