from world import GameWorld

class GameServer:
    def __init__(self):
        self.world = GameWorld()
        self.input_buffer = {}

    def receive_input(self, player_id, input_data):
        self.input_buffer[player_id] = input_data

    def tick(self):
        self.world.update(self.input_buffer)
        self.input_buffer = {}