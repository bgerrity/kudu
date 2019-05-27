import sys, os, json, time

import requests

sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec
import lib.payload as pl

from client.packet import Packet as CPacket
from server.server import Server

C_COUNT = 2
S_COUNT = 3

# get some text dumps
with open("test/blackbird.txt", "rb") as f:
    address1, address2, body1, body2 = [ f.read(x) for x in (pl.ADDRESS_SIZE, pl.ADDRESS_SIZE, pl.MESSAGE_SIZE, pl.MESSAGE_SIZE) ]

# construct client packets
cpackets = [CPacket() for _ in range(C_COUNT)]
# print("a1", len(address1))
# print("a2", len(address2))
# print("b1", len(body1))

cpackets[0].payload = pl.export_payload(pl.Payload(address1, address2, body2))
cpackets[1].payload = pl.export_payload(pl.Payload(address2, address1, body1))

with open("server_keys.json") as f:
    keys = [k.encode() for k in json.loads(f.read())]

cpackets[0].client_prep_up(keys)
cpackets[1].client_prep_up(keys)

# serv.collect_request(b"0", cpackets[0].send_out())

requests.post('http://localhost:5001/submission/0', data=cpackets[0].send_out())
requests.post('http://localhost:5001/submission/1', data=cpackets[1].send_out())

time.sleep(3) # time to process

response = requests.get("http://localhost:5001/deaddrop/0")
cpackets[0].client_prep_down(response.content)

response = requests.get("http://localhost:5001/deaddrop/1")
cpackets[1].client_prep_down(response.content)

print("true is pass: be sure to read test/blackbird.txt")
print("client0", cpackets[0].send_out() == body1)
print("client1", cpackets[1].send_out() == body2)