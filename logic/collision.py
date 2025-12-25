import pygame


def check_rect_collision(rect1, rect2): # pretty damn useless function
    """
    Returns True if two rectangles overlap.
    """
    return rect1.colliderect(rect2) # prebuilt function in pygame


def resolve_platform_collision(player_rect, platform_rect, vel_x, vel_y):
    """
    Simple AABB collision resolution for platforms.
    Returns modified vel_x, vel_y and on_ground boolean.
    """
    on_ground = False

    if check_rect_collision(player_rect, platform_rect):
        # From top (landing on platform)
        if vel_y > 0 and player_rect.bottom > platform_rect.top:
            player_rect.bottom = platform_rect.top
            vel_y = 0
            on_ground = True

        # From bottom (hitting ceiling)
        elif vel_y < 0 and player_rect.top < platform_rect.bottom:
            player_rect.top = platform_rect.bottom
            vel_y = 0

        # From sides (horizontal collision)
        if vel_x > 0 and player_rect.right > platform_rect.left:
            player_rect.right = platform_rect.left
            vel_x = 0
        elif vel_x < 0 and player_rect.left < platform_rect.right:
            player_rect.left = platform_rect.right
            vel_x = 0

    return vel_x, vel_y, on_ground