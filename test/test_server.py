import sys, os, json

import requests

sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec
import lib.payload as pl

from client.packet import Packet as CPacket
from server.server import Server

C_COUNT = 2
S_COUNT = 3

# fix these values to ease interactions
pl.ADDRESS_SIZE = 3
pl.MESSAGE_SIZE = 10

# construct client packets
cpackets = [CPacket() for _ in range(C_COUNT)]
cpackets[0].payload = pl.export_payload(pl.Payload("foo".encode(), "bar".encode(), "saltywater".encode()))
cpackets[1].payload = pl.export_payload(pl.Payload("bar".encode(), "foo".encode(), "smeltysalt".encode()))

# run server which will generate key
serv = Server(client_count=C_COUNT, server_count=S_COUNT)

with open("server_keys.json") as f:
    keys = [k.encode() for k in json.loads(f.read())]

cpackets[0].client_prep_up(keys)
cpackets[1].client_prep_up(keys)

print(f"prior to collects round:{serv.current_round} state:{serv.mode}")

serv.collect_request(b"0", cpackets[0].send_out())
print(f"between collects. round:{serv.current_round} state:{serv.mode}")
serv.collect_request(b"1", cpackets[1].send_out())
print(f"after collects. round:{serv.current_round} state:{serv.mode}")

cpackets[0].client_prep_down(serv.return_request(b"0"))
print(f"between collects. round:{serv.current_round} state:{serv.mode}")
cpackets[1].client_prep_down(serv.return_request(b"1"))
print(f"after collects. round:{serv.current_round} state:{serv.mode}")

result0 = cpackets[0].send_out()
result1 = cpackets[1].send_out()

print(result0, result1)
