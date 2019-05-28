import sys, os, json

import requests

sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec

from client.packet import Packet as CPacket
from server.server import Packet as SPacket

from server.server import Bundle

# Simualates the lifecycle of a packet -- onioned, peeled layer by layer

C_COUNT = 7
S_COUNT = 9

# construct client packets
cpackets =  [CPacket() for _ in range(C_COUNT)]
for i, p in enumerate(cpackets):
    p.payload = f"I am packet {i}.".encode()

# generate server keys
rsa_keys = [ec.generate_rsa() for _ in range(S_COUNT)]
sbundles = [Bundle() for _ in range(S_COUNT)]

# onion clients up
rsa_pub_keys = [k.publickey().export_key() for k in rsa_keys]
for p in cpackets:
    p.client_prep_up(rsa_pub_keys)
cpackets_out = [p.send_out() for p in cpackets]
print("Client done.")

# worker servers

rsa_priv_keys = [k.export_key() for k in rsa_keys]

# sequentially process up
prev_out = cpackets_out
for b, pk in zip(sbundles, rsa_priv_keys):
    b.load_up(prev_out)
    prev_out = b.send_up(pk)

print("at term got:")
print(prev_out)

prev_out2 = prev_out
for b in reversed(sbundles): # go in the opposite direction now
    b.load_down(prev_out2)
    prev_out2 = b.send_down()

print("down done")

for p, r in zip(cpackets, prev_out2):
    p.client_prep_down(r)

print("at client got: (should have id ordered)")
print([p.send_out() for p in cpackets])