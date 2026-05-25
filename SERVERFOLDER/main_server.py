# main_server.py
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from network.server.server import GameServer

if __name__ == "__main__":
    server = GameServer(host="0.0.0.0", port=9999)
    server.run()