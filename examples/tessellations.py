import random
import sys
import math
import time

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal import *

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
pygame.display.set_caption("Tessellations")
clock = pygame.time.Clock()

dp = [0, 0]
mouse_pos = Vector2()
moving = False
alive = True
# end of basic config

camera = H2Camera(H2Vector(), H2Vector.FromHyperbolical(0, 1), zoom=0.95)
projection = GeneralPerspectiveModel(camera, Window_size, perspective_distance=1)
projection.cull_range = 4

disc: ProjectedCircle = projection.disc

layers = 7
p = 7
q = 3
position = H2Vector.FromHyperpolar(0.1, 0.01)
rotation = -math.tau / 4
draw_lines = False
cull = True

# its size increases with tesselation layers, as it's used for optimization of tesselation generation
# for p=4, q=5 you can see some of them not being used
visualize_lookup_tesselation = False
lookup_detail: int = 3
subdivide_lines: bool = True

coloring: int = 2  # 0-blue, 1-red, 2-green
draw_cam_lines = False

FloodTessellation.LOG_PROGRESS = True
tesselation = FloodTessellation(p, q, position, rotation, layers)
print(f"Tile count: {tesselation.tile_count}")
print(f"Lookup bins count: {tesselation.tile_lookup.bin_count}")

tilegons = tesselation.tile_polygons
cull_circles = tesselation.tile_circles

#circlegons = [c.approximate(30) for c in tesselation.tile_circles]
#inscribed_circlegons = [c.approximate(30) for c in tesselation.tile_inscribed_circles]
lines = tesselation.tile_forward_lines

polygons = tilegons
#polygons += circlegons
#polygons += inscribed_circlegons

if visualize_lookup_tesselation:
    lookup_gons = tesselation.tile_lookup.get_polygons(lookup_detail, subdivide_lines)
    polygons = lookup_gons
    cull_circles = list(map(lambda x: x.circle_hull, lookup_gons))
    #polygons = list(map(lambda c: c.approximate(10), cull_circles))

for i, polygon in enumerate(polygons):
    polygon.key = i
    cull_circles[i].key = i

for i, line in enumerate(lines):
    line.key = i + polygons[-1].key + 1

if coloring == 0:
    colors = [(random.randint(150, 255), random.randint(100, 200), random.randint(50, 100))
              for _ in range(lines[-1].key + 1)]
elif coloring == 1:
    colors = [(random.randint(50, 100), random.randint(150, 255), random.randint(150, 255))
              for _ in range(lines[-1].key + 1)]
elif coloring == 2:
    colors = [(random.randint(50, 200), random.randint(150, 255), random.randint(50, 150))
                  for _ in range(lines[-1].key + 1)]


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

    if draw_lines and not visualize_lookup_tesselation:
        if cull:
            projected_lines = projection.cull_and_project_lines(lines, cull_circles)
        else:
            projected_lines = projection.project_lines(lines)

        for line in projected_lines:
            pygame.draw.line(display, colors[line.key], line.a, line.b, 2)

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
