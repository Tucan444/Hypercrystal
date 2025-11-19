import random
import sys
import time

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal.projections import *
from hypercrystal import H2Transform, H2Vector
from hypercrystal.shapes import H2Line, H2Circle, ProjectedCircle, H2Polygon

import math

from hypercrystal.shapes import Hypercycle

from hypercrystal.shapes import ProjectedPolygon

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
projection = PointcareModel(camera, Window_size)
projection.cull_range = 4.5

disc: ProjectedCircle = projection.disc

# test for performance
render_circles: bool = True
render_circlons: bool = False

circles_n = 600
circlon_samples = 30

circles = [
    H2Circle(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   4.5*(2**random.uniform(0, 1))),
             random.uniform(0.2, 1.5), key=i)
    for i in range(circles_n)
]
colors = [(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
          for _ in range(len(circles)+1)]

circlons = [
    c.approximate(circlon_samples) for c in circles
]

t = time.time()
while alive:
    # blitting and drawing
    display.fill((40, 40, 40) if projection.disc_present else (20, 20, 20))

    if projection.disc_present:
        pygame.draw.circle(display, (20, 20, 20), disc.center, disc.radius)

    projection.update()

    circles_to_project = projection.cull_circles(circles)

    if render_circles:
        projected_circles = projection.project_circles(circles_to_project)
        for circle in projected_circles:
            pygame.draw.circle(display, colors[circle.key], circle.center, circle.radius)

    if render_circlons:
        projected_circlons: list[ProjectedPolygon]  = projection.project_polygons(
            [circlons[circle.key] for circle in circles_to_project]
        )
        for circlon in projected_circlons:
            pygame.draw.polygon(display, colors[circlon.key + 1], circlon.points)

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

    pygame.display.set_caption(f"fps: {1 / (time.time() - t)}")
    t = time.time()

    screen.blit(display, dp)
    pygame.display.update()
    clock.tick(120)
