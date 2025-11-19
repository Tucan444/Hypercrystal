import random
import sys
import math

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal.projections import *
from hypercrystal import H2Transform, H2Vector, H2Ray
from hypercrystal.shapes import H2Line, H2Circle, ProjectedCircle

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

camera = H2Camera(H2Vector(), H2Vector.FromHyperbolical(0, 0.5), zoom=0.95)
projection = GeneralPerspectiveModel(camera, Window_size, perspective_distance=0.5)

disc: ProjectedCircle = projection.disc


random_ray = H2Ray(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 3)),
                   H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                           random.uniform(0, 3)))

lines_n = 20
lines_raw = [
    H2Line(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 9)),
           H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 9))
           , (255, 100, 160))
    for i in range(lines_n)
]
lines_raw.append(random_ray.get_line(1))
lines_raw[-1].key = (150, 150, 220)

lines = [l.approximate(20) for l in lines_raw]

circles_n = 10
circles = [
    H2Circle(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(0, 9)), random.uniform(0.1, 0.5)
             , key=(240, 100, 80)).approximate(10)
    for _ in range(circles_n)
]

circles.append(H2Circle(random_ray.position, 0.05, key=(150, 150, 220)).approximate(15))

big_circle = H2Circle(H2Vector.FromHyperpolar(random.uniform(0, H2Transform.TAU),
                                   random.uniform(3, 6)), random.uniform(1.2, 1.8)
             , key=(26, 235, 193))
circles.append(big_circle.approximate(20))


while alive:
    # blitting and drawing
    display.fill((40, 40, 40))

    pygame.draw.circle(display, (20, 20, 20), disc.center, disc.radius)

    projection.update()

    projected_circles = projection.project_polygons(circles)
    for circle in projected_circles:
        pygame.draw.polygon(display, circle.key, circle.points)


    projected_lines = projection.project_polygons(lines)
    for line in projected_lines:
        for i in range(len(line.points) - 1):
            pygame.draw.line(display, line.key, line.points[i], line.points[i+1], 1)

    mouse_world_pos = projection.reproject(mouse_pos)
    if mouse_world_pos is not None:
        ray: H2Ray = H2Ray(camera.position, mouse_world_pos)
        t = None

        for line in lines_raw:
            new_t = ray.cast_against_line(line)
            if new_t is None:
                continue

            if t is None:
                t = new_t

            t = min(t, new_t)

        for polycircle in circles[:-1]:
            new_t = ray.cast_against_polygon(polycircle)
            if new_t is None:
                continue

            if t is None:
                t = new_t

            t = min(t, new_t)

        new_t = ray.duel(random_ray)
        if new_t is not None:
            if t is None:
                t = new_t

            t = min(t, new_t)

        new_t = ray.cast_against_circle(big_circle)

        if new_t is not None:
            if t is None:
                t = new_t

            t = min(t, new_t)

        if t is not None:
            end_position = projection.project(ray.sample(t))
            pygame.draw.line(display, (255, 255, 100), center, end_position, 3)

    cam_lines = [H2Line(camera.position, camera.up), H2Line(camera.position, camera.right)]
    for line in projection.project_lines(cam_lines):
        pygame.draw.line(display, (50, 240, 220), line.a, line.b, 2)

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
