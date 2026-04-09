import pygame
import socket
import json

SERVER_ADDR = ("localhost", 9999)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)

pygame.init()
screen = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()

state = {"players": {}}

running = True
while running:

    space_pressed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                space_pressed = True

    # send input
    msg = {"space": space_pressed}
    sock.sendto(json.dumps(msg).encode(), SERVER_ADDR)

    # receive state
    try:
        data, _ = sock.recvfrom(4096)
        state = json.loads(data.decode())
    except:
        pass

    screen.fill((30,30,30))

    # draw players
    for i, player_id in enumerate(state["players"]):
        p = state["players"][player_id]

        color = (255,0,0) if p["color"] == "red" else (0,0,255)

        pygame.draw.rect(
            screen,
            color,
            pygame.Rect(100 + i*200, 150, 80, 80)
        )

    pygame.display.flip()
    clock.tick(60)