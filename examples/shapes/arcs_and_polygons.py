import random
import sys

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal.projections import *
from hypercrystal import H2Transform, H2Vector
from hypercrystal.shapes import H2Line, H2Circle, ProjectedCircle, H2Polygon
from hypercrystal.shapes.arc import H2Arc

import math

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

subdivision_samples: int = 5

polygon = H2Polygon([
    H2Vector.FromHyperpolar(0, 0.8),
    H2Vector.FromHyperpolar(-0.8, 1),
    H2Vector.FromHyperpolar(-0.7, 0.5),
    H2Vector.FromHyperpolar(2.5, 1.1)]
)
polygon = polygon.subdivide(subdivision_samples)

polyline = H2Polygon(polygon.points.copy(), is_spline=True)
polyline = polyline.subdivide(subdivision_samples)

arcs_n = 10
arcs_raw = [
    H2Arc(
        H2Vector.FromHyperpolar(random.uniform(0, math.tau),
                                random.uniform(0, 2)),
        H2Vector.FromHyperpolar(random.uniform(0, math.tau),
                                random.uniform(0, 2)),
        random.uniform(-math.tau, math.tau)
    )
    for _ in range(arcs_n)
]

arcs = [a.approximate(30) for a in arcs_raw]


while alive:
    # blitting and drawing
    display.fill((20, 20, 20))

    projection.update()

    arcs_projected = projection.project_polygons(arcs)
    for arc in arcs_projected:
        for i in range(len(arc.points) - 1):
            pygame.draw.line(display, (255, 87, 66),
                             arc.points[i], arc.points[i + 1], 2)

    projected_polygon = projection.project_polygons([polygon])[0]
    pygame.draw.polygon(display, (255, 84, 118), projected_polygon.points)

    projected_polyline = projection.project_polygons([polyline])[0]
    for i in range(len(polyline.points)-1):
        pygame.draw.line(display, (84, 255, 254),
                         projected_polyline.points[i], projected_polyline.points[i+1], 2)

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
