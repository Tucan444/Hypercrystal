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

camera = H2Camera(H2Vector(), H2Vector.FromHyperbolical(0, 1), zoom=0.96)
projection = GeneralPerspectiveModel(camera, Window_size, perspective_distance=2)
projection.cull_range = 4

disc: ProjectedCircle = projection.disc

layers = 6
p = 4
q = 5
position = H2Vector.FromHyperpolar(0.1, 0.01)
rotation = -math.tau / 4
draw_lines = True

image_index = 1 # 0 - red square, 1 - blue rectangle
billboard_scale = 0.8
draw_cam_lines = False

FloodTessellation.LOG_PROGRESS = True
tesselation = FloodTessellation(p, q, position, rotation, layers)
print(f"Tile count: {tesselation.tile_count}")
print(f"Lookup bins count: {tesselation.tile_lookup.bin_count}")

lines = tesselation.tile_forward_lines

rays = [
    H2Ray(line.a, line.b) for line in lines
]

billboards = [
    H2Billboard(ray.position, ray.sample(tesselation.inscribed_radius*billboard_scale)) for ray in rays
]

images = [
    pygame.image.load("../media/example_assets/sandclock.png").convert(),
    pygame.image.load("../media/example_assets/waterstar.png").convert()
]


t = time.time()
dt = 0.01
while alive:
    # blitting and drawing
    display.fill((40, 40, 40))

    pygame.draw.circle(display, (20, 20, 20), disc.center, disc.radius)

    projection.update()

    for billboard in billboards:
        billboard.update(projection)
        billboard.blit(images[image_index], display)

    if draw_lines:
        projected_lines = projection.project_lines(lines)

        for line in projected_lines:
            pygame.draw.line(display, (255, 255, 70), line.a, line.b, 2)

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
