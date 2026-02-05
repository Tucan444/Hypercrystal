import math
import random
import sys

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal import H2Transform, H2Vector
from hypercrystal.operators import Collisions
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

lines_n = 5
circles_n = 3

lines_raw = [
    H2Line(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 3)),
           H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 3))
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

line_collisions: int = 0
line_circle_collisions: int = 0

for i, line in enumerate(lines_raw):
    for j, line_ in enumerate(lines_raw):
        if i == j:
            continue

        if Collisions.Process(line, line_):
            line_collisions += 1

    for circle in circles_raw:
        if Collisions.Process(line, circle):
            line_circle_collisions += 1

circle_collisions: int = 0
for i, circle in enumerate(circles_raw):
    for j, circle_ in enumerate(circles_raw):
        if i == j:
            continue

        if Collisions.Process(circle, circle_):
            circle_collisions += 1

line_collisions //= 2
circle_collisions //= 2

print(f"Found\n"
      f"Line Collisions: {line_collisions}, LineCircle Collisions: {line_circle_collisions}, "
      f"Circle Collisions: {circle_collisions}.")


while alive:
    # blitting and drawing
    display.fill((20, 20, 20))

    projection.update()

    projected_circles = projection.project_polygons(circles)
    for circle in projected_circles:
        pygame.draw.polygon(display, (160, 10, 180), circle.points)

    lines_projected = projection.project_polygons(lines)
    for line in lines_projected:
        for i in range(len(line.points) - 1):
            pygame.draw.line(display, (255, 100, 160), line.points[i], line.points[i + 1], 1)

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
