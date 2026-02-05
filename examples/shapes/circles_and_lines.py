import random
import sys

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal.projections import *
from hypercrystal import H2Transform, H2Vector
from hypercrystal.shapes import H2Line, H2Circle, ProjectedCircle

import math

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
projection = PointcareModel(camera, Window_size)

disc: ProjectedCircle = projection.disc

lines_n = 100
subdivided = True
lines = [
    H2Line(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 9)),
           H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 9))
           ).approximate(10)
    for _ in range(lines_n)
]

circles_n = 40
circles = [
    H2Circle(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 9)), random.uniform(0.2, 1.5)
             ).approximate(20)
    for _ in range(circles_n)
]


while alive:
    # blitting and drawing
    display.fill((40, 40, 40))

    pygame.draw.circle(display, (20, 20, 20), disc.center, disc.radius)

    projection.update()

    projected_circles = projection.project_polygons(circles)
    for circle in projected_circles:
        pygame.draw.polygon(display, (160, 100, 80), circle.points)


    projected_lines = projection.project_polygons(lines) if subdivided else projection.project_lines(lines)
    for line in projected_lines:
        if subdivided:
            for i in range(len(line.points) - 1):
                pygame.draw.line(display, (255, 100, 160), line.points[i], line.points[i+1], 1)
        else:
            pygame.draw.line(display, (255, 100, 160), line.a, line.b, 1)

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
