import sys, os, json
import os

import requests

sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec
from server.packet import Packet, Contents


# gen rsa keys
rsa_keys = [ec.generate_rsa(), ec.generate_rsa(), ec.generate_rsa()]

# generate rsa keys

rsa_pub_keys = [k.publickey().export_key() for k in rsa_keys]



# construct packet
c_packet = Packet(client=True)
c_packet.contents = Contents("12", "13", "my mother told me -- from 54") # collect, drop, message


# onionize
c_packet.client_prep_up(rsa_pub_keys)

rsa_priv_keys = [k.export_key() for k in rsa_keys]

c_packet.client = False

c_packet.symm_keys = None
c_packet.onion_peel_layer(rsa_priv_keys[2])

print("Pass one done.")

# exit()
c_packet.data = c_packet.payload
c_packet.payload = None
c_packet.symm_keys = None
c_packet.onion_peel_layer(rsa_priv_keys[1])

print("Pass two done.")

c_packet.data = c_packet.payload
c_packet.payload = None
c_packet.symm_keys = None
c_packet.onion_peel_layer(rsa_priv_keys[0])

print("Pass three done.")


print(vars(c_packet))
