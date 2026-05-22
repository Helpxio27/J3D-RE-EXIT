# config/controls.py
import pygame

CONTROLS = [
    {
        "left":      pygame.K_a,
        "right":     pygame.K_d,
        "jump":      pygame.K_w,
        "drop":      pygame.K_s,
        "use_power": pygame.K_e,     
    },
    # Universal second player controls
    #{
    #     "left":      pygame.K_d,
    #     "right":     pygame.K_g,
    #     "jump":      pygame.K_r,
    #     "drop":      pygame.K_f,
    #     "use_power": pygame.K_t,     
    # },
    {
        "left":      pygame.K_LEFT,
        "right":     pygame.K_RIGHT,
        "jump":      pygame.K_UP,
        "drop":      pygame.K_DOWN,
        "use_power": pygame.K_RCTRL, 
    }
]