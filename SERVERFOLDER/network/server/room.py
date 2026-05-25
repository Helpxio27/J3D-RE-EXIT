# network/server/room.py
from network.shared.protocol import MAX_PLAYERS_PER_ROOM
from network.shared.serialization import encode_ready, encode_state, encode_error
import pygame
import time

class Room:
    def __init__(self, code: str, sock, level_walls):
        self.code = code
        self.sock = sock
        self.level_walls = level_walls

        # { player_id: address }
        self.clients = {}

        # One sim per player slot — imported lazily to avoid circular imports
        from game.entities.player.sim import PlayerSim
        self.player_sims = [
            PlayerSim(500, 700, is_tagger=True),
            PlayerSim(300, 700, is_tagger=False),
        ]

        self.tick = 0
        self.started = False

        # Pending inputs for this tick { player_id: input_dict }
        self._pending_inputs = {}

        print(f"[ROOM {code}] Created")

    @property
    def is_full(self) -> bool:
        return len(self.clients) >= MAX_PLAYERS_PER_ROOM

    @property
    def is_empty(self) -> bool:
        return len(self.clients) == 0

    # =====================
    # DOES: registers a new player into this room
    # returns assigned player_id, or None if full
    # =====================
    def add_player(self, addr) -> int | None:
        if self.is_full:
            return None
        player_id = len(self.clients)
        self.clients[player_id] = addr
        print(f"[ROOM {self.code}] Player {player_id} joined from {addr}")

        # Tell the client their assigned ID
        self.sock.sendto(encode_ready(self.code, player_id), addr)

        # If room is now full, start the match
        if self.is_full:
            self._start()

        return player_id

    def _start(self):
        self.started = True
        print(f"[ROOM {self.code}] Match starting!")

    # =====================
    # DOES: queues an input for this tick
    # =====================
    def receive_input(self, player_id: int, input_dict: dict):
        self._pending_inputs[player_id] = input_dict

    # =====================
    # DOES: simulates one tick using pending inputs, broadcasts state
    # =====================
    def tick_update(self):
        if not self.started:
            return

        # Apply inputs to sims
        for i, sim in enumerate(self.player_sims):
            inp = self._pending_inputs.get(i, {
                "left": False, "right": False,
                "jump": False, "drop": False,
                "use_power": False
            })
            sim.update(self.level_walls, inp)

        # Tag logic
        self._update_tag()

        # Broadcast truth to all clients
        self._broadcast_state()

        self._pending_inputs.clear()
        self.tick += 1

    def _update_tag(self):
        tagger = next((p for p in self.player_sims if p.is_tagger), None)
        runner = next((p for p in self.player_sims if not p.is_tagger), None)
        if tagger and runner and tagger.can_tag(runner):
            tagger.is_tagger = False
            runner.is_tagger = True
            tagger.tagback_cooldown = tagger.tagback_cooldown_time
            runner.vel_x = 0
            runner.vel_y = 0
            runner.stun_timer = 10

    def _broadcast_state(self):
        packet = encode_state(self.code, self.tick, self.player_sims)
        for addr in self.clients.values():
            try:
                self.sock.sendto(packet, addr)
            except Exception:
                pass