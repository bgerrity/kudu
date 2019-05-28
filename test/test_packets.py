import sys, os, json

import requests

sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec

from client.packet import Packet as CPacket
from server.packet import Packet as SPacket

from lib import contents as wrap

# Simualates the lifecycle of a packet -- onioned, peeled layer by layer

# construct client packet
cpacket = CPacket()
contents = wrap.export_contents(wrap.Contents("12", "13", "my mother told me -- from 54")) # collect, drop, message
cpacket.payload = contents

# generate server keys
rsa_keys = [ec.generate_rsa() for _ in range(3)]

# three packet/servers
spackets = [SPacket() for _ in rsa_keys]

# generate pub keys and onion up
rsa_pub_keys = [k.publickey().export_key() for k in rsa_keys]
cpacket.client_prep_up(rsa_pub_keys)
print("Client done.")

# worker servers

rsa_priv_keys = [k.export_key() for k in rsa_keys]

spackets[0].load_up(cpacket.send_out())
spackets[0].onion_peel_layer(rsa_priv_keys[0])
print("Pass one done.")

spackets[1].load_up(spackets[0].send_out())
spackets[1].onion_peel_layer(rsa_priv_keys[1])
print("Pass two done.")

spackets[2].load_up(spackets[1].send_out())
spackets[2].onion_peel_layer(rsa_priv_keys[2])
print("Pass three done.")

term_collected = spackets[2].send_out()
result = json.loads(term_collected)["message"]
print(f"term message:{result}")



down_send = "fe fi fo fum".encode()
spackets[2].load_down(down_send)
spackets[2].onion_add_layer()

spackets[1].load_down(spackets[2].send_out())
spackets[1].onion_add_layer()

spackets[0].load_down(spackets[1].send_out())
spackets[0].onion_add_layer()

down_collected = spackets[0].send_out()
cpacket._inbox = down_collected
cpacket.onion_decrypt_symm()

print(f"down_dec:{cpacket.send_out().decode()}")
