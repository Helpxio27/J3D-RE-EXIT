# network/shared/serialization.py
import json
from network.shared.protocol import MSG_INPUT, MSG_STATE, MSG_JOIN, MSG_READY, MSG_ERROR

def encode_join(room_code: str, player_id: int) -> bytes:
    return json.dumps({
        "type":      MSG_JOIN,
        "room":      room_code.upper(),
        "player_id": player_id
    }).encode()

def encode_input(room_code: str, player_id: int, tick: int, input_dict: dict) -> bytes:
    return json.dumps({
        "type":      MSG_INPUT,
        "room":      room_code.upper(),
        "tick":      tick,
        "player_id": player_id,
        "input":     input_dict
    }).encode()

def encode_state(room_code: str, tick: int, player_sims: list) -> bytes:
    return json.dumps({
        "type":    MSG_STATE,
        "room":    room_code.upper(),
        "tick":    tick,
        "players": [sim.to_dict(player_id=i) for i, sim in enumerate(player_sims)]
    }).encode()

def encode_ready(room_code: str, assigned_id: int) -> bytes:
    return json.dumps({
        "type":      MSG_READY,
        "room":      room_code.upper(),
        "player_id": assigned_id   # server tells client which player they are
    }).encode()

def encode_error(message: str) -> bytes:
    return json.dumps({
        "type":    MSG_ERROR,
        "message": message
    }).encode()

def decode(data: bytes) -> dict | None:
    try:
        return json.loads(data.decode())
    except Exception:
        return None

def needs_correction(sim, server_data: dict, threshold: float) -> bool:
    dx = abs(sim.rect.x - server_data["x"])
    dy = abs(sim.rect.y - server_data["y"])
    return dx > threshold or dy > threshold