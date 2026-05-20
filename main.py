# main.py
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from game.app import App

if __name__ == "__main__":
    app = App()
    app.run()