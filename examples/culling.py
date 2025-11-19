import random
import sys
import math

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal.projections import *
from hypercrystal import H2Transform, H2Vector
from hypercrystal.shapes import H2Line, H2Circle, ProjectedCircle
from hypercrystal.shapes import Hypercycle

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

camera = H2Camera(H2Vector(), H2Vector.FromHyperbolical(0, 0.5), zoom=0.95)
projection = GeneralPerspectiveModel(camera, Window_size, 3 )
projection.cull_range = 4

disc: ProjectedCircle = projection.disc

line = H2Line(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 3)),
           H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 3)))

hypercycles_n = 2
max_distance = 3
step_size = (2 * max_distance) / (hypercycles_n - 1)
hypercycles_raw = [
    Hypercycle(line, -max_distance + step_size * i, (0.2, 0.8), i)
    for i in range(hypercycles_n)
]
hypercycles = [h.approximate(30) for h in hypercycles_raw]

linegon = line.approximate(20)
line_hull = linegon.circle_hull

hhull = hypercycles_raw[0].circle_hull

circles_n = 200
circles_raw = [
    H2Circle(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   4*(2**random.uniform(0, 1))),
             random.uniform(0.2, 1.5), i
             )
    for i in range(circles_n)
]

hhull.key = len(circles_raw)
circles_raw.append(hhull)
line_hull.key = len(circles_raw)
circles_raw.append(line_hull)

a = H2Circle(hypercycles_raw[0].sample(0), 0.1)
a.key = len(circles_raw)
circles_raw.append(a)

b = H2Circle(hypercycles_raw[0].sample(1), 0.1)
b.key = len(circles_raw)
circles_raw.append(b)

c = H2Circle(hypercycles_raw[0].sample(0.5), 0.1)
c.key = len(circles_raw)
circles_raw.append(c)

circles = [circle.approximate(60) for circle in circles_raw]
colors = [(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
          for _ in range(len(circles_raw))]

while alive:
    # blitting and drawing
    display.fill((40, 40, 40) if projection.disc_present else (20, 20, 20))

    if projection.disc_present:
        pygame.draw.circle(display, (20, 20, 20), disc.center, disc.radius)

    projection.update()

    cull_circle = projection.project_polygons([projection.cull_circle.approximate(40)])[0]
    pygame.draw.polygon(display, (10, 10, 10), cull_circle.points)

    for circle in projection.cull_and_project_polygons(circles, circles_raw):
        pygame.draw.polygon(display, colors[circle.key], circle.points)

    projected_h = projection.project_polygons(hypercycles)

    if projection.to_not_cull_circle(hhull):
        for hypercycle in projected_h:
            for i in range(len(hypercycle.points) - 1):
                pygame.draw.line(display, (255, 100, 160),
                                 hypercycle.points[i], hypercycle.points[i + 1], 1)
            break

    if projection.to_not_cull_circle(line_hull):
        main_line = projection.project_polygons([linegon])[0]
        for i in range(len(main_line.points) - 1):
            pygame.draw.line(display, (255, 200, 60),
                             main_line.points[i], main_line.points[i + 1], 1)

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
