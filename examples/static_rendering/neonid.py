import random
import sys
import math
import time

import pygame

from hypercrystal import *

# config
image_size = (1920 * 2, 1080 * 2)
filename = "3_tower2.png"
img = pygame.Surface(image_size)

bg_color = (0, 0, 0)
space_color = (20, 20, 20)

camera = H2Camera(H2Vector(), H2Vector.FromHyperbolical(0, 1), zoom=0.95)
projection = GeneralPerspectiveModel(camera, image_size, perspective_distance=2)
disc: ProjectedCircle = projection.disc

minimum_tessellation_polygons_n = 6000
p_bound = (3, 3)
q_bound = (3, 30)

tessellation_position = H2Vector.FromHyperpolar(0.1, 0.01)
tessellation_rotation = -math.tau / 4
coloring: int = 2  # 0-red, 1-blue, 2-green
wireframe_width = 1

FloodTessellation.LOG_PROGRESS = True

# end of config
assert 0 <= coloring <= 2

valid_tessellations = [
    (p, q)
    for p in range(p_bound[0], p_bound[1] + 1)
    for q in range(q_bound[0], q_bound[1] + 1)
    if FloodTessellation.check_validity(p, q)
]
print(f"Constructing {len(valid_tessellations)} tessellations: {valid_tessellations}")

tessellations = [
    FloodTessellation(p, q, tessellation_position, tessellation_rotation, 0)
    for p, q in valid_tessellations
]

for i, tessellation in enumerate(tessellations):
    while tessellation.tile_count < minimum_tessellation_polygons_n:
        tessellation.generate_layer()

    print(f"{i+1}/{len(tessellations)} constructed")

print("Generating polygons")
tessellation_polygons = []

for i, tessellation in enumerate(tessellations):
    tessellation_polygons.append(tessellation.tile_polygons)
    print(f"{i + 1}/{len(tessellations)} generated")

i = 0
for polygons in tessellation_polygons:
    for polygon in polygons:
        polygon.key = i
        i += 1

tile_count = sum(list(map(len, tessellation_polygons)))
largest_tesselation_tile_count = max(list(map(len, tessellation_polygons)))
print(f"Tile count: {tile_count}")

print("Generating colors")
if coloring == 0:
    colors = [(random.randint(150, 255), random.randint(100, 200), random.randint(50, 100))
              for _ in range(tile_count)]
elif coloring == 1:
    colors = [(random.randint(50, 100), random.randint(150, 255), random.randint(150, 255))
              for _ in range(tile_count)]
elif coloring == 2:
    colors = [(random.randint(50, 200), random.randint(150, 255), random.randint(50, 150))
                  for _ in range(tile_count)]

print("Drawing base bg")
img.fill(bg_color)

if type(projection) in [GeneralPerspectiveModel, PointcareModel, KleinModel]:
    pygame.draw.circle(img, space_color, disc.center, disc.radius)
else:
    img.fill(space_color)

print("Projecting polygons")
projected_polygons = [
    projection.project_polygons(polygons)
    for polygons in tessellation_polygons
]

print("Drawing fractal")
for polygons in projected_polygons:
    for polygon in polygons:
        pygame.draw.polygon(img, colors[polygon.key], polygon.points, wireframe_width)


print("Saving image")
pygame.image.save(img, f"rendered/{filename}")
