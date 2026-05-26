# network/client/client.py
import socket
from network.shared.serialization import encode_input, encode_join, decode, needs_correction
from network.shared.protocol import (
    MSG_STATE, MSG_READY, MSG_ERROR,
    SERVER_IP, SERVER_PORT, CORRECTION_THRESHOLD
)


class GameClient:
    def __init__(self):
        self.server_addr = (SERVER_IP, SERVER_PORT)
        self.room_code   = None
        self.player_id   = None   # assigned by server on join
        self.tick        = 0
        self.connected   = False
        self.error       = None   # last error message from server

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)

        self._input_history = {}
        self.match_started = False
        
    # =====================
    # DOES: sends join request for a room code
    # =====================
    def join(self, room_code: str):
        self.room_code = room_code.upper()
        packet = encode_join(self.room_code, 0)  # id 0, server will assign real one
        self.sock.sendto(packet, self.server_addr)
        print(f"[CLIENT] Sent join to {self.server_addr} room={self.room_code}")
        
    # =====================
    # DOES: sends local input to server
    # =====================
    def send_input(self, input_dict: dict):
        if not self.connected or not self.room_code:
            return
        self._input_history[self.tick] = input_dict
        packet = encode_input(self.room_code, self.player_id, self.tick, input_dict)
        try:
            self.sock.sendto(packet, self.server_addr)
        except Exception:
            pass
        self.tick += 1

        cutoff = self.tick - 120
        self._input_history = {
            k: v for k, v in self._input_history.items() if k >= cutoff
        }

    # =====================
    # DOES: sends an event (like power use) to the server
    # =====================
    def send_event(self, event_type: str, data: dict):
        if not self.connected or not self.room_code:
            return
        from network.shared.serialization import encode_event
        packet = encode_event(self.room_code, self.player_id, event_type, data)
        try:
            self.sock.sendto(packet, self.server_addr)
        except Exception:
            pass

    # =====================
    # DOES: reads all pending packets
    # returns list of decoded messages
    # =====================
    def receive(self) -> list:
        messages = []
        while True:
            try:
                data, _ = self.sock.recvfrom(4096)
                msg = decode(data)
                if not msg:
                    continue

                # Handle ready + error here directly
                if msg["type"] == MSG_READY:
                    self.player_id = msg["player_id"]
                    self.connected = True
                    print(f"[CLIENT] Joined as player {self.player_id}")            
                    print(f"[CLIENT] Got READY — player_id={self.player_id} room={self.room_code}")

                elif msg["type"] == MSG_ERROR:
                    self.error = msg["message"]
                    print(f"[CLIENT] Error: {self.error}")

                else:
                    messages.append(msg)

            except BlockingIOError:
                break
            except Exception:
                break
        return messages

    # =====================
    # DOES: applies server correction to a sim if needed
    # =====================
    def apply_correction(self, sim, server_player_data: dict):
        if needs_correction(sim, server_player_data, CORRECTION_THRESHOLD):
            sim.from_dict(server_player_data)

    def disconnect(self):
        self.sock.close()