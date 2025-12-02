import pygame
from src.game import Game 

def main():
    pygame.init()
    Game().run()
    pygame.quit()

if __name__ == "__main__":
    main()
