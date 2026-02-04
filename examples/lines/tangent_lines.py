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

angle_at_horizon: float = 1.2
length_of_lines = 3
lines_n = 60

lines_raw = [H2Line(
H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 4)),
H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 4))
)]

for i in range(lines_n - 1):
    lines_raw.append(H2Line.TangentAtT(lines_raw[0], random.uniform(0, 1)))

for line in lines_raw[1:]:
    line.set_length(length_of_lines, True)

lines = [
    line.approximate(20)
    for line in lines_raw
]

tangent_line: H2Line = H2Line(H2Vector(), H2Vector.FromHyperpolar(0.5, 0.2))
lines.append(tangent_line.approximate(30))


while alive:
    # blitting and drawing
    display.fill((80, 80, 160))

    pygame.draw.circle(display, (20, 20, 40), disc.center, disc.radius)

    projection.update()

    projected_lines = projection.project_polygons(lines)
    for j, line in enumerate(projected_lines):
        for i in range(len(line.points) - 1):
            if i == 0:
                color = (250, 250, 100)
            else:
                color = (255, 100, 160)

            if j == 0:
                color = (color[0], color[1], 255)
            elif j == len(projected_lines)-1:
                color = (color[0], 255, color[2])

            pygame.draw.line(display, color, line.points[i], line.points[i+1], 1)

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

            reprojected_mouse_pos: H2Vector = projection.reproject(mouse_pos)

            if reprojected_mouse_pos is not None:
                tangent_line = H2Line.TangentToPoint(lines_raw[0], reprojected_mouse_pos)

                if tangent_line is not None:
                    lines[-1] = tangent_line.approximate(len(lines[-1].points))

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
