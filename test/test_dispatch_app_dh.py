import sys, os, json, time

import requests

sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec
import lib.payload as pl

from client.packet import Packet as CPacket
from server.server import Server

priv = ec.generate_dh()
pub = ec.export_dh_public(priv)

# step up for reasons
requests.post('http://localhost:5000/increment_users')
requests.post('http://localhost:5000/increment_users')

send = b"dog"

requests.post('http://localhost:5000/publish_DH_key/0', data=pub)

time.sleep(3) # time to process

response = requests.get("http://localhost:5000/get_DH_key/0")
key_returned = response.content

print("type:", type(key_returned))
print("len:", len(key_returned))

print("pub:", send)
print("key_returned:", key_returned)

print("true is pass")
print("result:", key_returned == pub)