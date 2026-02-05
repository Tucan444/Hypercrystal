import math
import random
import sys

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal import H2Transform, H2Vector
from hypercrystal.operators import Intersections
from hypercrystal.projections import *
from hypercrystal.shapes import H2Line, H2Circle, ProjectedCircle, H2Polygon

# basic config
pygame.mixer.pre_init(48000, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(16)
available = pygame.font.get_fonts()

Window_size = (900, 700)
Default_size = Window_size
center: Vector2 = Vector2(Window_size[0] // 2, Window_size[1] // 2)
screen = pygame.display.set_mode(Window_size)
display = pygame.Surface(Window_size)
pygame.display.set_caption("Name")
clock = pygame.time.Clock()

dp = [0, 0]
mouse_pos = Vector2()
moving = False
alive = True
# end of basic config

camera = H2Camera(H2Vector(), H2Vector.FromHyperbolical(0, 1), zoom=0.4)
projection = GansModel(camera, Window_size)

disc: ProjectedCircle = projection.disc

subdivision_samples: int = 5
lines_n = 10
circles_n = 3

polygon = H2Polygon([
    H2Vector.FromHyperpolar(0, 0.8),
    H2Vector.FromHyperpolar(-0.8, 1),
    H2Vector.FromHyperpolar(-0.7, 0.5),
    H2Vector.FromHyperpolar(2.5, 1.1)]
)
polygon = polygon.subdivide(subdivision_samples)

polyline = H2Polygon(polygon.points.copy(), is_spline=True)
polyline = polyline.subdivide(subdivision_samples)

lines_raw = [
    H2Line(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 6)),
           H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 6))
           )
    for _ in range(lines_n)
]

lines = [a.approximate(20) for a in lines_raw]

circles_raw = [
    H2Circle(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 2)), random.uniform(0.2, 0.6)
             )
    for _ in range(circles_n)
]
circles = [c.approximate(30) for c in circles_raw]

polygon2 = H2Polygon([
    H2Vector.FromHyperpolar(0.9, 0.8),
    H2Vector.FromHyperpolar(-0.8, 1.2),
    H2Vector.FromHyperpolar(-0.4, 1.3)]
)
polygon2 = polygon2.subdivide(3)

intersections = []

for i, line in enumerate(lines_raw):
    for j, line_ in enumerate(lines_raw):
        if i == j:
            continue

        intersections += Intersections.LineLine(line, line_)

    for circle in circles_raw:
        intersections += Intersections.LineCircle(line, circle)

    pin = Intersections.LinePolygon(line, polygon)
    intersections += [inter for i in pin for inter in i[1]]

    pin = Intersections.LinePolygon(line, polygon2)
    intersections += [inter for i in pin for inter in i[1]]

for i, circle in enumerate(circles_raw):
    for j, circle_ in enumerate(circles_raw):
        if i == j:
            continue

        intersections += Intersections.CircleCircle(circle_, circle)

    pin = Intersections.CirclePolygon(circle, polygon)
    intersections += [inter for i in pin for inter in i[1]]

    pin = Intersections.CirclePolygon(circle, polygon2)
    intersections += [inter for i in pin for inter in i[1]]

ppin = Intersections.PolygonPolygon(polygon, polygon2)
intersections += [inter for i in ppin for inter in i[2]]


while alive:
    # blitting and drawing
    display.fill((20, 20, 20))

    projection.update()

    projected_circles = projection.project_polygons(circles)
    for circle in projected_circles:
        pygame.draw.polygon(display, (160, 100, 80), circle.points)

    lines_projected = projection.project_polygons(lines)
    for line in lines_projected:
        for i in range(len(line.points) - 1):
            pygame.draw.line(display, (255, 100, 160), line.points[i], line.points[i + 1], 1)

    projected_polygon = projection.project_polygons([polygon])[0]
    pygame.draw.polygon(display, (255, 84, 118), projected_polygon.points)

    projected_polygon = projection.project_polygons([polygon2])[0]
    pygame.draw.polygon(display, (255, 180, 118), projected_polygon.points)

    projected_polyline = projection.project_polygons([polyline])[0]
    for i in range(len(polyline.points)-1):
        pygame.draw.line(display, (84, 255, 254),
                         projected_polyline.points[i], projected_polyline.points[i+1], 2)

    projected_intersections = projection.project_points(intersections)
    for p in projected_intersections:
        pygame.draw.circle(display, (100, 250, 200), p, 5)

    if moving:
        theta = math.atan2(mouse_pos.y - center.y, mouse_pos.x - center.x)
        camera.move_by_theta(theta, 1/60)

    # event loop

    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = Vector2(mouse_pos[0] - dp[0], mouse_pos[1] - dp[1])
            moving = True
        elif event.type == MOUSEBUTTONUP:
            moving = False


        elif event.type == MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = Vector2(mouse_pos[0] - dp[0], mouse_pos[1] - dp[1])
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit(0)

        elif event.type == QUIT:
            pygame.quit()
            sys.exit(0)

    # basic loop config

    screen.blit(display, dp)
    pygame.display.update()
    clock.tick(60)
