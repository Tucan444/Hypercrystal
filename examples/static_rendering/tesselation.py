import random
import sys
import math
import time

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal import *

# end of basic config
image_size = (1920 * 4, 1080 * 4)
filename = "3_7_22-layers.png"
img = pygame.Surface(image_size)

bg_color = (0, 0, 0)
space_color = (20, 20, 20)

camera = H2Camera(H2Vector(), H2Vector.FromHyperbolical(0, 1), zoom=0.95)
projection = GeneralPerspectiveModel(camera, image_size, perspective_distance=2)
disc: ProjectedCircle = projection.disc

layers = 22
p = 3
q = 7

position = H2Vector.FromHyperpolar(0.1, 0.01)
tessellation_rotation = -math.tau / 4
coloring: int = 0  # 0-red, 1-blue, 2-green

FloodTessellation.LOG_PROGRESS = True
tesselation = FloodTessellation(p, q, position, tessellation_rotation, layers)
print(f"Tile count: {tesselation.tile_count}")
print(f"Lookup bins count: {tesselation.tile_lookup.bin_count}")

tilegons = tesselation.tile_polygons
polygons = tilegons

for i, polygon in enumerate(polygons):
    polygon.key = i

if coloring == 0:
    colors = [(random.randint(150, 255), random.randint(100, 200), random.randint(50, 100))
              for _ in range(polygons[-1].key + 1)]
elif coloring == 1:
    colors = [(random.randint(50, 100), random.randint(150, 255), random.randint(150, 255))
              for _ in range(polygons[-1].key + 1)]
elif coloring == 2:
    colors = [(random.randint(50, 200), random.randint(150, 255), random.randint(50, 150))
                  for _ in range(polygons[-1].key + 1)]

img.fill(bg_color)

if type(projection) in [GeneralPerspectiveModel, PointcareModel, KleinModel]:
    pygame.draw.circle(img, space_color, disc.center, disc.radius)
else:
    img.fill(space_color)

projected_polygons = projection.project_polygons(polygons)

for tile in projected_polygons:
    pygame.draw.polygon(img, colors[tile.key], tile.points)

pygame.image.save(img, f"rendered/{filename}")
