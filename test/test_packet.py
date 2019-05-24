import sys, os, json

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

print("FeeFee:")
# print(server2.payload)

# print(f"resulting payload at terminal:{server2.payload}")


# print(f"s2.symm:{server2.symm_keys}")
# print(f"s2.payload:{server2.payload}")

# enc = ec.encrypt_aes(server2.payload, server2.symm_keys)
# print(enc)

# enc2 = ec.encrypt_aes(enc, server1.symm_keys)

# dec2 = ec.decrypt_aes(enc2, server1.symm_keys)

# dec = ec.decrypt_aes(dec2, server2.symm_keys)
# print(dec)


server2.payload = "fe fi fo fum".encode()
server2.onion_add_layer()

server1.payload = server2.data
server1.onion_add_layer()

server0.payload = server1.data
server0.onion_add_layer()

# print("FooFoo:")
# print(server0.data)
# exit()

# print(server1.data)
# exit()
c_packet.data = server0.data

c_packet.onion_decrypt_symm()
print(f"payload final:{c_packet.payload}")
# print(vars(server2))
















# print("Pass two done.")

# c_packet.data = c_packet.payload
# c_packet.payload = None
# c_packet.symm_keys = None
# c_packet.onion_peel_layer(rsa_priv_keys[0])

# print("Pass three done.")


# print(vars(c_packet))
