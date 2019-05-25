import sys, os, json

import requests

sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec
from server.packet import Packet, Contents
from client.packet import Packet as CPacket

# Simualates the lifecycle of a packet -- onioned, peeled layer by layer

# construct packet
c_packet = CPacket(client=True)
c_packet.contents = Contents("12", "13", "my mother told me -- from 54") # collect, drop, message

rsa_keys = [ec.generate_rsa() for _ in range(3)]


# three packet/servers and pub keys
server0 = Packet()
server1 = Packet()
server2 = Packet()

# generate pub keys and onion up
rsa_pub_keys = [k.publickey().export_key() for k in rsa_keys]
c_packet.client_prep_up(rsa_pub_keys)
print("Client done.")

# print(vars(c_packet))

rsa_priv_keys = [k.export_key() for k in rsa_keys]

server0.load_up(c_packet.data)
server0.onion_peel_layer(rsa_priv_keys[0])
print("Pass one done.")

server1.load_up(server0.send_out())
server1.onion_peel_layer(rsa_priv_keys[1])
print("Pass two done.")

server2.load_up(server1.send_out())
server2.onion_peel_layer(rsa_priv_keys[2])
print("Pass three done.")

term_collected = server2.send_out()
result = json.loads(term_collected)["message"]
print(f"term message:{result}")



down_send = "fe fi fo fum".encode()
server2.load_down(down_send)
server2.onion_add_layer()

server1.load_down(server2.send_out())
server1.onion_add_layer()

server0.load_down(server1.send_out())
server0.onion_add_layer()

down_collected = server0.send_out()
c_packet.data = down_collected
c_packet.onion_decrypt_symm()

print(f"down_dec:{c_packet.payload.decode()}")
