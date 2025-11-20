import math
import random
import sys
import time

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal import H2Vector, H2Transform
from hypercrystal.misc.h2_lookup import H2Lookup
from hypercrystal.projections import *
from hypercrystal.shapes import H2Line, ProjectedCircle

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
projection = GeneralPerspectiveModel(camera, Window_size, perspective_distance=2)
projection.cull_range = 5

disc: ProjectedCircle = projection.disc

point_count: int = 2_000
lookup_detail: int = 5
subdivide_lines: bool = False
cull = True

draw_cam_lines = False
shards = False
position = H2Vector.FromHyperpolar(0.4, 0)
mover = H2Transform.StraightToA(position)

lookup: H2Lookup[None] = H2Lookup()
for _ in range(point_count):
    point: H2Vector = H2Vector.FromHyperpolar(
                            random.uniform(0, math.tau),
                            2**random.uniform(0, 3.5) - 1)
    lookup[mover @ point] = None

print(f"Lookup bins count: {lookup.bin_count}")

lookup_gons = lookup.get_polygons(lookup_detail, subdivide_lines)
polygons = lookup_gons
cull_circles = list(map(lambda x: x.circle_hull, lookup_gons))

if shards:
    polygons = list(map(lambda c: c.approximate(lookup_detail*3), cull_circles))

for i, polygon in enumerate(polygons):
    polygon.key = i
    cull_circles[i].key = i

colors = [(random.randint(150, 255), random.randint(50, 100), random.randint(150, 255))
          for _ in range(len(polygons))]


t = time.time()
dt = 0.01
while alive:
    # blitting and drawing
    display.fill((40, 40, 40))

    pygame.draw.circle(display, (20, 20, 20), disc.center, disc.radius)

    projection.update()

    if cull:
        projected_polygons = projection.cull_and_project_polygons(polygons, cull_circles)
    else:
        projected_polygons = projection.project_polygons(polygons)

    for tile in projected_polygons:
        pygame.draw.polygon(display, colors[tile.key], tile.points)

    if draw_cam_lines:
        cam_lines = [H2Line(camera.position, camera.up), H2Line(camera.position, camera.right)]
        for line in projection.project_lines(cam_lines):
            pygame.draw.line(display, (50, 240, 220), line.a, line.b, 2)

    if moving:
        theta = math.atan2(mouse_pos.y - center.y, mouse_pos.x - center.x)
        camera.move_by_theta(theta, dt)

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
    dt = time.time() - t
    t = time.time()

    screen.blit(display, dp)
    pygame.display.update()
    clock.tick(60)
