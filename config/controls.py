# config/controls.py
import pygame

CONTROLS = [
    {
        "left":  pygame.K_a,
        "right": pygame.K_d,
        "jump":  pygame.K_w,
        "drop":  pygame.K_s
    },
    {
        "left":  pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump":  pygame.K_UP,
        "drop":  pygame.K_DOWN
    }
]