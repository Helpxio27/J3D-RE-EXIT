# server.py
import socket
import json
import time

SERVER_ADDR = ("localhost", 9999)
TICK_RATE = 60

# Game state
state = {
    "players": [
        {"x": 300, "y": 300, "is_tagger": True},
        {"x": 500, "y": 300, "is_tagger": False},
    ]
}

# define object sock, from socket library
# AF_INET -> Ipv4 address specification
# SOCK_DGRAM -> UDP, SOCK_STREAM -> TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
# Make the new object sock get a server address
sock.bind(SERVER_ADDR) 
# Blocking of connections set to off / makes command RECVFROM() not freeze if not data is recieved for a while
sock.setblocking(False) 

clients = {}  # maps client addr -> player index

print("Server running on", SERVER_ADDR)

while True:
    start_time = time.time()

    # Receive inputs
    # Example of the try syntax :
    # try:
    #     x = int("123")
    # except ValueError:
    #     print("Not a number")
    # else:
    #     print("Success! Number is", x)
    # finally:
    #     print("This runs no matter what")


    try: # save execute
        while True:
            data, addr = sock.recvfrom(1024) #DATA: data received, ADDR: the guy who sent it
            inp = json.loads(data.decode()) # decodes the data and puts it in INP in string
            
            # server.py
            if addr not in clients: # if they aren't already on the client list
                clients[addr] = len(clients) # add at the end of the list
                idx = clients[addr] # if they aren't enough player slots:
                if idx >= len(state["players"]):
                    # create a new player slot with default values
                    state["players"].append({
                        "x": 400,
                        "y": 300,
                        "is_tagger": False  # default value
                    })
            
            idx = clients[addr] # 
            # Simple movement
            if inp.get("left"): state["players"][idx]["x"] -= 5
            if inp.get("right"): state["players"][idx]["x"] += 5
            if inp.get("jump"): state["players"][idx]["y"] -= 5
            if inp.get("drop"): state["players"][idx]["y"] += 5

    except BlockingIOError: # if no data
        pass  # no data this tick ... YEAHHHH

    # Send updated state to all clients
    for addr in clients:
        sock.sendto(json.dumps(state).encode(), addr)

    # Tick control
    elapsed = time.time() - start_time
    time.sleep(max(0, 1/TICK_RATE - elapsed))