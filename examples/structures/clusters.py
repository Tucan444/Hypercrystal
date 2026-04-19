import random
import sys
import math
import time

import pygame
from pygame import Vector2, Surface
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
projection = PointcareModel(camera, Window_size)
projection.cull_range = 4

disc: ProjectedCircle = projection.disc

draw_clusters: bool = False
k_clusters: int = 4
steps: int = 5
leaf_n: int = 10

layers = 9
p = 7
q = 3
position = H2Vector.FromHyperpolar(0.1, 0.01)
rotation = -math.tau / 4
cull_using_cluster: bool=True

# its size increases with tesselation layers, as it's used for optimization of tesselation generation
# for p=4, q=5 you can see some of them not being used
visualize_lookup_tesselation = False
lookup_detail: int = 3
subdivide_lines: bool = True

coloring: int = 2  # 0-red, 1-blue, 2-green
draw_cam_lines = False

FloodTessellation.LOG_PROGRESS = True

t = time.time()
tesselation = FloodTessellation(p, q, position, rotation, layers)
print(f"Tile count: {tesselation.tile_count}")
print(f"Lookup bins count: {tesselation.tile_lookup.bin_count}")
print(f"Tiling generation took: {time.time() - t}s")

tilegons = tesselation.tile_polygons
cull_circles = tesselation.tile_circles


t = time.time()
cluster = H2Cluster.clusterize(cull_circles, k_clusters, steps, leaf_n)
print(f"Cluster generation took: {time.time() - t}s")

cluster_circles: list[H2Circle] = cluster.circles_visual

#circlegons = [c.approximate(30) for c in tesselation.tile_circles]
#inscribed_circlegons = [c.approximate(30) for c in tesselation.tile_inscribed_circles]

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

if coloring == 0:
    colors = [(random.randint(150, 255), random.randint(100, 200), random.randint(50, 100))
              for _ in range(cull_circles[-1].key + 1)]
elif coloring == 1:
    colors = [(random.randint(50, 100), random.randint(150, 255), random.randint(150, 255))
              for _ in range(cull_circles[-1].key + 1)]
elif coloring == 2:
    colors = [(random.randint(50, 200), random.randint(150, 255), random.randint(50, 150))
                  for _ in range(cull_circles[-1].key + 1)]


t = time.time()
dt = 0.01
while alive:
    # blitting and drawing
    display.fill((40, 40, 40))

    pygame.draw.circle(display, (20, 20, 20), disc.center, disc.radius)

    projection.update()

    if not draw_clusters:
        if cull_using_cluster:
            surviving_circles = projection.cull_cluster(cluster)
            projected_polygons = [projection.project_polygon(polygons[circle.key]) for circle in surviving_circles]
            for tile in projected_polygons:
                pygame.draw.polygon(display, colors[tile.key], tile.points)
        else:
            projected_polygons = projection.cull_and_project_polygons(polygons, cull_circles)
            for tile in projected_polygons:
                pygame.draw.polygon(display, colors[tile.key], tile.points)

    else:
        projected_circles = projection.project_circles(cluster_circles)
        for i, circle in enumerate(projected_circles):
            circle_surface: Surface = Surface((round(circle.radius*2 + 1), round(circle.radius*2 + 1)))
            pygame.draw.circle(circle_surface, colors[i % len(colors)], (circle.radius, circle.radius), circle.radius)

            circle_surface.set_colorkey((0, 0, 0))
            circle_surface.set_alpha(100)
            display.blit(circle_surface, circle.center - Vector2(circle.radius, circle.radius))

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
    clock.tick(1020)
