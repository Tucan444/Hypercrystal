import math
import random
import sys

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal import H2Vector
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

camera = H2Camera(H2Vector(), H2Vector.FromHyperbolical(0, 1), zoom=0.95)
projection = GeneralPerspectiveModel(camera, Window_size, 1 )

disc: ProjectedCircle = projection.disc

samples_n: int = 20
radius: float = 0.5
circles: list[H2Polygon] = [
    H2Circle(H2Vector(), radius).approximate(samples_n)
]
colors: list = [(255, 255, 255)]

while alive:
    # blitting and drawing
    display.fill((40, 40, 40) if projection.disc_present else (20, 20, 20))

    if projection.disc_present:
        pygame.draw.circle(display, (20, 20, 20), disc.center, disc.radius)

    projection.update()

    projected_circles = projection.project_polygons(circles)
    for i, circle in enumerate(projected_circles):
        pygame.draw.polygon(display, colors[i], circle.points)

    if moving:
        theta = math.atan2(mouse_pos.y - center.y, mouse_pos.x - center.x)
        camera.move_by_theta(theta, 1/60)

    # event loop

    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = Vector2(mouse_pos[0] - dp[0], mouse_pos[1] - dp[1])

            mouse_world_pos: H2Vector = projection.reproject(mouse_pos)
            if mouse_world_pos is not None:
                circles.append(H2Circle(mouse_world_pos, radius).approximate(samples_n))
                colors.append((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
            else:
                print("World pos of mouse is None")

        elif event.type == MOUSEBUTTONUP:
            pass

        elif event.type == MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = Vector2(mouse_pos[0] - dp[0], mouse_pos[1] - dp[1])
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit(0)

            if event.key == K_SPACE:
                moving = True

        elif event.type == KEYUP:
            if event.key == K_SPACE:
                moving = False

        elif event.type == QUIT:
            pygame.quit()
            sys.exit(0)

    # basic loop config

    screen.blit(display, dp)
    pygame.display.update()
    clock.tick(60)
