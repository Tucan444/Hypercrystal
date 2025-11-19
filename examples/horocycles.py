import math
import random
import sys

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal import H2Vector
from hypercrystal.projections import *
from hypercrystal.shapes import H2Line, H2Circle, ProjectedCircle
from hypercrystal.shapes.horocycle import Horocycle

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
projection = GeneralPerspectiveModel(camera, Window_size, perspective_distance=1)

disc: ProjectedCircle = projection.disc

horocycles_n = 20
alpha = random.uniform(0, math.tau)
horocycles_raw = [
    Horocycle(alpha, H2Vector.FromHyperpolar(
        alpha,
        random.uniform(-4, 4)
    ), (-5, 5), i)
    for i in range(horocycles_n)
]

horocycles = [h.approximate(30) for h in horocycles_raw]
anchors = [H2Circle(h.anchor, 0.05, h.key).approximate(6) for h in horocycles_raw]

colors = [(random.randint(100, 255), random.randint(10, 100), random.randint(100, 255))
          for _ in range(len(horocycles))]

horizon_circle = H2Circle(H2Vector.FromHyperpolar(alpha, 7), 0.6)
horizon_circle = horizon_circle.approximate(20)


while alive:
    # blitting and drawing
    display.fill((40, 40, 40))

    pygame.draw.circle(display, (20, 20, 20), disc.center, disc.radius)

    projection.update()

    projected_horocycles = projection.project_polygons(horocycles)
    for horocycle in projected_horocycles:
        for i in range(len(horocycle.points) - 1):
            pygame.draw.line(display, colors[horocycle.key],
                             horocycle.points[i], horocycle.points[i+1], 1)

    projected_anchors = projection.project_polygons(anchors)
    for anchor in projected_anchors:
        pygame.draw.polygon(display, colors[anchor.key - 1], anchor.points)

    projected_horizon = projection.project_polygons([horizon_circle])[0]
    pygame.draw.polygon(display, (82, 160, 255), projected_horizon.points)

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
