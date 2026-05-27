# main.py
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pygame
from game.app import App
from game.scenes.intro_scene import IntroScene

if __name__ == "__main__":
    app = App()
    # Replace initial menu scene with intro
    from game.scenes.intro_scene import IntroScene
    app.scene_stack = [IntroScene(app)]
    app.run()