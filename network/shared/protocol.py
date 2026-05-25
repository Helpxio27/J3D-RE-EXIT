# network/shared/protocol.py

MSG_INPUT  = "input"
MSG_STATE  = "state"
MSG_JOIN   = "join"
MSG_READY  = "ready"
MSG_EVENT  = "event"
MSG_ERROR  = "error"

EVT_POWER_USED  = "power_used"
EVT_BOMB_THROWN = "bomb_thrown"
EVT_LASER_FIRED = "laser_fired"
EVT_TAG         = "tag"

CORRECTION_THRESHOLD = 8
MAX_PLAYERS_PER_ROOM = 2
CODE_LENGTH = 4
SERVER_IP = "37.59.121.134" # VPS IP
SERVER_PORT = 25001