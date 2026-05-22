# network/server/server.py
import socket
import time
import random
import string
from network.shared.serialization import decode, encode_error
from network.shared.protocol import MSG_INPUT, MSG_JOIN, SERVER_PORT, CODE_LENGTH


def generate_code(existing_codes: set) -> str:
    """Generates a unique 4-letter room code"""
    while True:
        code = "".join(random.choices(string.ascii_uppercase, k=CODE_LENGTH))
        if code not in existing_codes:
            return code


class GameServer:
    def __init__(self, host: str = "0.0.0.0", port: int = SERVER_PORT):
        self.host = host
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.sock.setblocking(False)

        # { room_code: Room }
        self.rooms = {}

        # Placeholder walls — replace with actual map loading later
        self.level_walls = []

        print(f"[SERVER] Running on {host}:{port}")

    # =====================
    # DECIDES: routes incoming packets to the right room
    # =====================
    def _handle_packet(self, data: bytes, addr):
        msg = decode(data)
        if not msg:
            return

        msg_type = msg.get("type")
        room_code = msg.get("room", "").upper()

        if msg_type == MSG_JOIN:
            self._handle_join(room_code, addr)

        elif msg_type == MSG_INPUT:
            room = self.rooms.get(room_code)
            if room:
                room.receive_input(msg["player_id"], msg["input"])

    # =====================
    # DOES: creates or joins a room
    # =====================
    def _handle_join(self, room_code: str, addr):
        # Create room if it doesn't exist
        if room_code not in self.rooms:
            from network.server.room import Room
            self.rooms[room_code] = Room(room_code, self.sock, self.level_walls)

        room = self.rooms[room_code]

        if room.is_full:
            self.sock.sendto(encode_error("Room is full"), addr)
            return

        room.add_player(addr)

    # =====================
    # DOES: main server loop
    # =====================
    def run(self):
        from config.settings import FIXED_DT
        tick_duration = FIXED_DT
        last_tick = time.time()

        while True:
            # Read all pending packets
            while True:
                try:
                    data, addr = self.sock.recvfrom(4096)
                    self._handle_packet(data, addr)
                except BlockingIOError:
                    break
                except Exception:
                    break

            # Tick all active rooms
            now = time.time()
            if now - last_tick >= tick_duration:
                for code, room in list(self.rooms.items()):
                    room.tick_update()
                    # Clean up empty rooms
                    if room.is_empty:
                        del self.rooms[code]
                        print(f"[SERVER] Room {code} removed")
                last_tick = now

            time.sleep(0.001)


if __name__ == "__main__":
    server = GameServer()
    server.run()