import pygame
from player import Player  

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Test Player")

clock = pygame.time.Clock()

controls = {
    "left": pygame.K_q,
    "right": pygame.K_d,
    "jump": pygame.K_SPACE,
    "dash": pygame.K_LSHIFT
}

player = Player((100, 300), (0, 150, 255), controls)

# Plateformes
platforms = [
    Platform(0, 550, 800, 50),
    Platform(300, 450, 200, 20),
    Platform(100, 350, 150, 20)
]

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    player.update(keys, platforms)

    screen.fill((30, 30, 30))

    for p in platforms:
        screen.blit(p.image, p.rect)

    screen.blit(player.image, player.rect)

    pygame.display.flip()

pygame.quit()
