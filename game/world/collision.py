import pygame

def circle_rect_collision(circle_pos, radius, rect) -> bool: # -> bool | just an indicator that it should return bool ( optional )
    closest_x = max(rect.left, min(circle_pos[0], rect.right))
    closest_y = max(rect.top, min(circle_pos[1], rect.bottom))
    dx = circle_pos[0] - closest_x
    dy = circle_pos[1] - closest_y
    return (dx * dx + dy * dy) <= radius * radius

def resolve_horizontal(rect, obstacles, vel_x):
    on_wall = False
    wall_dir = 0
    for obstacle in obstacles:
        if rect.colliderect(obstacle):
            if vel_x > 0:
                rect.right = obstacle.left
                wall_dir = 1
            elif vel_x < 0:
                rect.left = obstacle.right
                wall_dir = -1
            vel_x = 0
            on_wall = True
    return vel_x, on_wall, wall_dir

def resolve_vertical(rect, obstacles, vel_y):
    on_ground = False
    for obstacle in obstacles:
        if rect.colliderect(obstacle):
            if vel_y > 0:
                rect.bottom = obstacle.top
                vel_y = 0
                on_ground = True
            elif vel_y < 0:
                rect.top = obstacle.bottom
                vel_y = 0
    return vel_y, on_ground