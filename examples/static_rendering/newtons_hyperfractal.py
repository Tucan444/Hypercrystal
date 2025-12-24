import random
import sys
import math
import time

import pygame
from pygame import Vector2
from pygame.locals import *

from hypercrystal import *

# this one was heavily assisted by AI, other scripts are mostly handwritten
image_size = (1280, 720)
filename = "newton2.png"
img = pygame.Surface(image_size)

bg_color = (0, 0, 0)
space_color = (20, 20, 20)
fractal_color = (255, 0, 70)
undecided_color = (255, 0, 75)
iterations = 20

root1 = Vector2(0, 0.6)
root2 = Vector2(math.tau * (5/12), 0.6)
root3 = Vector2(math.tau * (7/12), 0.6)

root_colors = [(234, 54, 70), (218, 234, 54), (247, 148, 69)]
shadow_color = (20, 20, 20)

camera = H2Camera(H2Vector(), H2Vector.FromHyperbolical(0, 1), zoom=2**0)
camera.move_left(0.5)

projection = HyperpolarModel(camera, image_size)
disc: ProjectedCircle = projection.disc

# end of config

r1=root1; r2=root2; r3=root3

r1_vec = H2Vector.FromHyperpolar(*r1)
r2_vec = H2Vector.FromHyperpolar(*r2)
r3_vec = H2Vector.FromHyperpolar(*r3)

r1_proj = projection.project(r1_vec)
r2_proj = projection.project(r2_vec)
r3_proj = projection.project(r3_vec)

C = Vector2(r1.x + r2.x + r3.x, r1.y * r2.y * r3.y)
C_subtractor = H2Transform.StraightToOrigin(H2Vector.FromHyperpolar(*C))

r12 = Vector2(r1.x * r2.x, r1.y * r2.y)
r13 = Vector2(r1.x * r3.x, r1.y * r3.y)
r23 = Vector2(r2.x * r3.x, r2.y * r3.y)

r12_transform = H2Transform.StraightToA(H2Vector.FromHyperpolar(*r12))
r13_transform = H2Transform.StraightToA(H2Vector.FromHyperpolar(*r13))
r23_transform = H2Transform.StraightToA(H2Vector.FromHyperpolar(*r23))
B_adder = r12_transform @ r13_transform @ r23_transform
B = Vector2(*(B_adder @ H2Vector()).hyperpolar)

r1_transform = H2Transform.StraightToA(r1_vec)
r2_transform = H2Transform.StraightToA(r2_vec)
r3_transform = H2Transform.StraightToA(r3_vec )
A_adder = r1_transform @ r2_transform @ r3_transform
A = Vector2(*(A_adder @ H2Vector()).hyperpolar)
A2 = Vector2(A.x, 2 * A.y)

def P(x: Vector2) -> Vector2:
    # x**3 in hyperpolar: (3 * theta, alpha**3)
    x3 = Vector2(3 * x.x, x.y ** 3)
    
    # x**2 in hyperpolar: (2 * theta, alpha**2)
    x2 = Vector2(2 * x.x, x.y ** 2)
    
    # x**2 * A in hyperpolar: multiply coordinates
    x2_A = Vector2(x2.x + A.x, x2.y * A.y)
    
    # x * B in hyperpolar: multiply coordinates
    x_B = Vector2(x.x + B.x, x.y * B.y)
    
    # Convert to H2Vector for hyperbolic operations
    x3_vec = H2Vector.FromHyperpolar(*x3)
    x2_A_vec = H2Vector.FromHyperpolar(*x2_A)
    x_B_vec = H2Vector.FromHyperpolar(*x_B)
    C_vec = H2Vector.FromHyperpolar(*C)
    
    # P(x) = x**3 - x**2 * A + x*B - C
    # Start with x**3
    result = x3_vec
    
    # Subtract x**2 * A (pull x2_A to origin)
    x2_A_subtractor = H2Transform.StraightToOrigin(x2_A_vec)
    result = x2_A_subtractor @ result
    
    # Add x*B (pull origin to x_B)
    x_B_adder = H2Transform.StraightToA(x_B_vec)
    result = x_B_adder @ result
    
    # Subtract C (pull C to origin) - C_subtractor is already defined
    result = C_subtractor @ result
    
    # Convert back to hyperpolar Vector2
    return Vector2(*result.hyperpolar)

def P_prime(x: Vector2) -> Vector2:
    # x**2 * 3 in hyperpolar: (2 * theta, 3 * alpha**2)
    x2_3 = Vector2(2 * x.x, 3 * (x.y ** 2))
    
    # x * A2 in hyperpolar: multiply coordinates
    x_A2 = Vector2(x.x + A2.x, x.y * A2.y)
    
    # Convert to H2Vector for hyperbolic operations
    x2_3_vec = H2Vector.FromHyperpolar(*x2_3)
    x_A2_vec = H2Vector.FromHyperpolar(*x_A2)
    
    # P'(x) = x**2 * 3 - x*A2 + B
    # Start with x**2 * 3
    result = x2_3_vec
    
    # Subtract x*A2 (pull x_A2 to origin)
    x_A2_subtractor = H2Transform.StraightToOrigin(x_A2_vec)
    result = x_A2_subtractor @ result
    
    # Add B (pull origin to B) - B_adder is already defined
    result = B_adder @ result
    
    # Convert back to hyperpolar Vector2
    return Vector2(*result.hyperpolar)

def step(x: Vector2) -> Vector2:
    MAX_ALPHA = 4.5
    if x.y > MAX_ALPHA:
        x = Vector2(x.x, MAX_ALPHA)
    
    # Compute P(x) and P'(x)
    P_x = P(x)
    P_prime_x = P_prime(x)

    if P_prime_x.y < 1e-10:
        P_prime_x = Vector2(P_prime_x.x, 1e-10)
    
    # P(x) / P'(x) in hyperpolar: (theta_P - theta_P', alpha_P / alpha_P')
    P_div_P_prime = Vector2(P_x.x - P_prime_x.x, P_x.y / P_prime_x.y)
    
    # Clamp result alpha
    if P_div_P_prime.y > MAX_ALPHA:
        P_div_P_prime = Vector2(P_div_P_prime.x, MAX_ALPHA)
    
    # Convert to H2Vector for hyperbolic operations
    x_vec = H2Vector.FromHyperpolar(*x)
    P_div_P_prime_vec = H2Vector.FromHyperpolar(*P_div_P_prime)
    
    # step(x) = x - (P(x) / P'(x))
    # Start with x
    result = x_vec
    
    # Subtract P(x) / P'(x) (pull P_div_P_prime to origin)
    P_div_P_prime_subtractor = H2Transform.StraightToOrigin(P_div_P_prime_vec)
    result = P_div_P_prime_subtractor @ result
    
    return Vector2(*result.hyperpolar)

def classify(x: H2Vector) -> int:
    dist1 = x.distance_to(r1_vec)
    dist2 = x.distance_to(r2_vec)
    dist3 = x.distance_to(r3_vec)

    if dist1 <= dist2 and dist1 <= dist3:
        return 0
    elif dist2 <= dist3:
        return 1
    else:
        return 2


colors1 = [(random.randint(150, 255), random.randint(100, 200), random.randint(50, 100))
          for _ in range(iterations)]
colors2 = [(random.randint(50, 100), random.randint(150, 255), random.randint(150, 255))
          for _ in range(iterations)]
colors3 = [(random.randint(50, 200), random.randint(150, 255), random.randint(50, 150))
              for _ in range(iterations)]

img.fill(bg_color)

if type(projection) in [GeneralPerspectiveModel, PointcareModel, KleinModel]:
    pygame.draw.circle(img, space_color, disc.center, disc.radius)
else:
    img.fill(space_color)

for y in range(image_size[1]):
    for x in range(image_size[0]):
        position: H2Vector = projection.reproject(Vector2(x, y))

        if position is None:
            continue

        z = Vector2(*position.hyperpolar)

        # Track classification streak
        current_index = None
        streak = 0
        
        for i in range(iterations):
            z = step(z)
            
            # Classify at each step
            z_vec = H2Vector.FromHyperpolar(*z)
            root_index = classify(z_vec)

            # Update streak
            if current_index == root_index:
                streak += 1
            else:
                current_index = root_index
                streak = 1
        
        # Use the colors array based on final index, with streak as the index
        colors_array = [colors1, colors2, colors3][current_index]
        streak_index = min(streak - 1, len(colors_array) - 1)
        pixel_color = colors_array[streak_index]
        
        img.set_at((x, y), pixel_color)


    print(f"row {y+1}/{image_size[1]} done")


r = image_size[1] // 100
r_black = r + 2

pygame.draw.circle(img, shadow_color, r1_proj, r_black)
pygame.draw.circle(img, shadow_color, r2_proj, r_black)
pygame.draw.circle(img, shadow_color, r3_proj, r_black)

pygame.draw.circle(img, colors1[0], r1_proj, r)
pygame.draw.circle(img, colors2[0], r2_proj, r)
pygame.draw.circle(img, colors3[0], r3_proj, r)

pygame.image.save(img, f"rendered/{filename}")
