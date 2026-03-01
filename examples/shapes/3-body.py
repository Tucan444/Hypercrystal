import random
import sys
import time

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal.projections import *
from hypercrystal import H2Transform, H2Vector
from hypercrystal.shapes import H2Line, H2Circle, ProjectedCircle, H2Polygon

import math

from hypercrystal.shapes import Hypercycle

from hypercrystal.shapes import ProjectedPolygon

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
projection = PointcareModel(camera, Window_size)

disc: ProjectedCircle = projection.disc

a_position: H2Vector = H2Vector.FromHyperpolar(0.5, random.uniform(1, 2))
b_position: H2Vector = H2Vector.FromHyperpolar(2.5, random.uniform(1, 2))
c_position: H2Vector = H2Vector.FromHyperpolar(4.7, random.uniform(1, 2))

a_radius: float = random.uniform(0.2, 0.6)
b_radius: float = random.uniform(0.2, 0.6)
c_radius: float = random.uniform(0.2, 0.6)

A: H2Circle = H2Circle(a_position, a_radius)
B: H2Circle = H2Circle(b_position, b_radius)
C: H2Circle = H2Circle(c_position, c_radius)

def random_offset(v: H2Vector):
    random_vector: H2Vector = H2Vector.FromHyperpolar(random.uniform(0, math.tau),
                                                      random.uniform(0, 0.5))
    transform: H2Transform = H2Transform.PointInverse(v)
    return transform @ random_vector

a_velocity: H2Vector = random_offset(a_position)
b_velocity: H2Vector = random_offset(b_position)
c_velocity: H2Vector = random_offset(c_position)

def update_positions():
    global a_velocity, b_velocity, c_velocity

    G: float = 1
    dt = 1 / 60

    gravity: callable = lambda a, b: (G * b.area) / (0.5 + math.sinh(a.center.distance_to(b.center)))

    a_velocity = H2Transform.AtoB(A.center, B.center, gravity(A, B) * dt) @ a_velocity
    a_velocity = H2Transform.AtoB(A.center, C.center, gravity(A, C) * dt) @ a_velocity

    b_velocity = H2Transform.AtoB(B.center, A.center, gravity(B, A) * dt) @ b_velocity
    b_velocity = H2Transform.AtoB(B.center, C.center, gravity(B, C) * dt) @ b_velocity

    c_velocity = H2Transform.AtoB(C.center, A.center, gravity(C, A) * dt) @ c_velocity
    c_velocity = H2Transform.AtoB(C.center, B.center, gravity(C, B) * dt) @ c_velocity

    a_move: H2Transform = H2Transform.LerpAB(A.center, a_velocity, dt)
    b_move: H2Transform = H2Transform.LerpAB(B.center, b_velocity, dt)
    c_move: H2Transform = H2Transform.LerpAB(C.center, c_velocity, dt)

    a_velocity = a_move @ a_velocity
    A.center = a_move @ A.center

    b_velocity = b_move @ b_velocity
    B.center = b_move @ B.center

    c_velocity = c_move @ c_velocity
    C.center = c_move @ C.center


while alive:
    # blitting and drawing
    display.fill((40, 40, 40) if projection.disc_present else (20, 20, 20))

    if projection.disc_present:
        pygame.draw.circle(display, (20, 20, 20), disc.center, disc.radius)

    update_positions()
    projection.update()

    projected_circles = projection.project_circles([A, B, C])
    for i, circle in enumerate(projected_circles):
        pygame.draw.circle(display, (250, i * 120, 0), circle.center, circle.radius)

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
    clock.tick(120)
