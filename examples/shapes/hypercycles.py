import random
import sys

import pygame
from pygame import Vector2
from pygame.locals import *
from hypercrystal.projections import *
from hypercrystal import H2Transform, H2Vector
from hypercrystal.shapes import H2Line, ProjectedCircle

import math

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

camera = H2Camera(H2Vector(), H2Vector.FromHyperbolical(0, 1), zoom=0.95)
projection = GeneralPerspectiveModel(camera, Window_size, 1)

disc: ProjectedCircle = projection.disc

subdivided = True
line = H2Line(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 4)),
           H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 4)))

hypercycles_n = 30
max_distance = 3
step_size = (2 * max_distance) / (hypercycles_n - 1)
hypercycles = [
    Hypercycle(line, -max_distance + step_size * i, (-1, 2)).approximate(50)
    for i in range(hypercycles_n)
]

linegon = line.approximate(20)

while alive:
    # blitting and drawing
    display.fill((40, 40, 40))

    pygame.draw.circle(display, (20, 20, 20), disc.center, disc.radius)

    projection.update()

    projected_h = projection.project_polygons(hypercycles)
    for hypercycle in projected_h:
        for i in range(len(hypercycle.points) - 1):
            pygame.draw.line(display, (255, 100, 160),
                             hypercycle.points[i], hypercycle.points[i+1], 1)

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
