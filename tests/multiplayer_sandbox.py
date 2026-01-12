import pygame
from player_minimal import Player

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Multiplayer Sandbox")
clock = pygame.time.Clock()

players = [
    Player(
        100, 100,
        controls={
            "left": pygame.K_a,
            "right": pygame.K_d,
            "up": pygame.K_w,
            "down": pygame.K_s
        },
        color=(255, 70, 70)
    ),
    Player(
        300, 100,
        controls={
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "up": pygame.K_UP,
            "down": pygame.K_DOWN
        },
        color=(70, 70, 255)
    )
]

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for p in players:
        p.update()

    screen.fill((25, 25, 25))
    for p in players:
        p.draw(screen)

    pygame.display.flip()

pygame.quit()
