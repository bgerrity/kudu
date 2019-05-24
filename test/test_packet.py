import sys, os, json
import os

import requests

sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec
from server.packet import Packet, Contents

# Simualates the lifecycle of a packet -- onioned, peeled layer by layer

# construct packet
c_packet = Packet(client=True)
c_packet.contents = Contents("12", "13", "my mother told me -- from 54") # collect, drop, message

rsa_keys = [ec.generate_rsa() for _ in range(3)]


# three packet/servers and pub keys
server0 = Packet(origin=True)
server1 = Packet()
server2 = Packet(terminal=True)

# generate pub keys and onion up
rsa_pub_keys = [k.publickey().export_key() for k in rsa_keys]
c_packet.client_prep_up(rsa_pub_keys)
print("Client done.")

# print(vars(c_packet))

rsa_priv_keys = [k.export_key() for k in rsa_keys]

server0.data = c_packet.data
server0.onion_peel_layer(rsa_priv_keys[0])
print("Pass one done.")

server1.data = server0.payload
server1.onion_peel_layer(rsa_priv_keys[1])
print("Pass two done.")

server2.data = server1.payload
server2.onion_peel_layer(rsa_priv_keys[2])
print("Pass three done.")

print(f"resulting payload:{server2.payload}")




# print("Pass two done.")

# c_packet.data = c_packet.payload
# c_packet.payload = None
# c_packet.symm_keys = None
# c_packet.onion_peel_layer(rsa_priv_keys[0])

# print("Pass three done.")


# print(vars(c_packet))
