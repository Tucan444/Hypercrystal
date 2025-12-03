import random
import sys
import math
import time

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal import *

# end of basic config
image_size = (1920, 1080)
filename = "ultrabrot.png"
img = pygame.Surface(image_size)

bg_color = (0, 0, 0)
space_color = (20, 20, 20)
fractal_color = (255, 0, 70)
undecided_color = (255, 0, 75)
iterations = 60
power = 4

camera = H2Camera(H2Vector(), H2Vector.FromHyperbolical(0, 1), zoom=2**-0.3)
camera.move_left(0)

projection = HyperpolarModel(camera, image_size)
disc: ProjectedCircle = projection.disc

coloring = 2 # 0 red, 1 blue, 2 green

# end of config

if coloring == 0:
    colors = [(random.randint(150, 255), random.randint(100, 200), random.randint(50, 100))
              for _ in range(iterations)]
elif coloring == 1:
    colors = [(random.randint(50, 100), random.randint(150, 255), random.randint(150, 255))
              for _ in range(iterations)]
elif coloring == 2:
    colors = [(random.randint(50, 200), random.randint(150, 255), random.randint(50, 150))
                  for _ in range(iterations)]

img.fill(bg_color)

if type(projection) in [GeneralPerspectiveModel, PointcareModel, KleinModel]:
    pygame.draw.circle(img, space_color, disc.center, disc.radius)
else:
    img.fill(space_color)

for y in range(image_size[1]):
    for x in range(image_size[0]):
        position = projection.reproject(Vector2(x, y))

        if position is None:
            continue

        z = H2Vector()
        adder = H2Transform.StraightToA(position)
        escape: int = -1

        for i in range(iterations):
            if z.alpha > 2:
                escape = i
                break

            z = H2Vector.FromHyperpolar(z.theta * power, z.alpha ** power)
            z = adder @ z

        if z.alpha <= 2:
            img.set_at((x, y), fractal_color)
        elif escape >= 0:
            img.set_at((x, y), colors[escape])
        else:
            img.set_at((x, y), undecided_color)

    print(f"row {y+1}/{image_size[1]} done")

pygame.image.save(img, f"rendered/{filename}")
