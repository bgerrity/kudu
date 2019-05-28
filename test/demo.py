import sys, os, json, time
from http import HTTPStatus

import requests

sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec
import lib.payload as pl

from client.packet import Packet as CPacket

# get some text dumps
with open("test/blackbird.txt", "rb") as f:
    address1, address2 = [ f.read(x) for x in (pl.ADDRESS_SIZE, pl.ADDRESS_SIZE) ]

def loop(id):
    while True:
        curr_round = requests.get("http://localhost:5001/current_round").text
        message = input(f"ID:{id} Round:{curr_round} Message $> ")
        
        cpacket = CPacket()

        # conversant
        if int(id) == 0:
            payload = pl.Payload(address1, address2, message.ljust(512).encode())
        elif int(id) == 1:
            payload = pl.Payload(address2, address1, message.ljust(512).encode())
            
        cpacket.payload = pl.export_payload(payload)


        with open("server_keys.json") as f:
            keys = [k.encode() for k in json.loads(f.read())]

        cpacket.client_prep_up(keys)

        requests.post(f"http://localhost:5001/submission/{id}", data=cpacket.send_out())

        # busy wait

        response = requests.get(f"http://localhost:5001/deaddrop/{id}")

        while response.status_code != HTTPStatus.OK:
            time.sleep(2)
            print("waiting for server")
            response = requests.get(f"http://localhost:5001/deaddrop/{id}")

        cpacket.client_prep_down(response.content)

        print(f"[{time.strftime('%a %H:%M:%S')}] {cpacket.send_out().decode().strip()}")

if __name__ == "__main__":
    id = sys.argv[1]

    loop(id)



# requests.post('http://localhost:5001/submission/0', data=cpackets[0].send_out())
# requests.post('http://localhost:5001/submission/1', data=cpackets[1].send_out())

# time.sleep(3) # time to process

# 
# cpackets[0].client_prep_down(response.content)

# response = requests.get("http://localhost:5001/deaddrop/1")
# cpackets[1].client_prep_down(response.content)

# print("true is pass: be sure to read test/blackbird.txt")
# print("client0", cpackets[0].send_out() == body1)
# print("client1", cpackets[1].send_out() == body2)