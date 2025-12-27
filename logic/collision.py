import pygame

def check_rect_collision(rect1, rect2): # pretty damn useless function
    """
    Returns True if two rectangles overlap.
    """
    return rect1.colliderect(rect2) # prebuilt function in pygame

def resolve_collision_x(player_rect, collider, vel_x):
    """
    collsion horizontale, les murs
    """
    on_wall = False
    wall_dir = 0

    if player_rect.colliderect(collider):       #si le joueur touche un collider
        if vel_x > 0:                             # collision en allant vers la droite
            player_rect.right=collider.left     # ke joueur se colle a un mur
            wall_dir = 1
        elif vel_x < 0:                           # collision allant vers la gauche
            player_rect.left=collider.right
            vel_y = -1

        vel_x = 0                 # stop le mouvement horizontal
        on_wall = True    

    return vel_x, on_wall, wall_dir


def resolve_collision_y(player_rect, collider, vel_y):
    """
    collision verticale, les murs
    """
    on_ground = False

    if player_rect.colliderect(collider):       #si le joueur tombe sur le collider
        if vel_y > 0:                            
            player_rect.bottom=collider.top     
            vel_y = 0  
            on_ground = True
        elif vel_y < 0:                           # le joueur touch le plafond
            player_rect.top = collider.bottom
            vel_y = 0

    return vel_y, on_ground







    
