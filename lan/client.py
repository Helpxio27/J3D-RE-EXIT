# client.py
import pygame
import socket
import json
import threading


SERVER_ADDR = ("localhost", 9999)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

player_state = [{"x":0,"y":0},{"x":0,"y":0}]

# Thread to receive state from server
def recv_thread():
    global player_state
    while True:
        try:
            data, _ = sock.recvfrom(2048)
            player_state = json.loads(data.decode())
        except:
            pass

threading.Thread(target=recv_thread, daemon=True).start()

running = True
while running:
    keys = pygame.key.get_pressed()
    inp = {
        "left": keys[pygame.K_a],
        "right": keys[pygame.K_d],
        "jump": keys[pygame.K_w],
        "drop": keys[pygame.K_s]
    }

    sock.sendto(json.dumps(inp).encode(), SERVER_ADDR)

    # Receive state from server
    try:
        data_bytes, _ = sock.recvfrom(4096)
        player_state = json.loads(data_bytes.decode())
    except:
        player_state = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30,30,30))

    # Draw players
    for p in player_state:
        is_tagger = p.get("is_tagger", False)
        color = (255, 255, 0) if is_tagger else (50, 50, 255)
        pygame.draw.rect(screen, color, pygame.Rect(p["x"], p["y"], 30, 30))

    pygame.display.flip()
    clock.tick(60)