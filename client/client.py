#! /usr/bin/env python3
# client/client.py

from http import HTTPStatus
import requests

import os, sys, time, json

sys.path.append(os.path.abspath('../Kudu'))

import lib.easy_crypto as ec
import lib.payload as pl

from packet import Packet

dispatch_port = None
server_port = None

self_id = None
partner_id = None

key_rsa = ec.generate_rsa()
key_dh = ec.generate_dh()

partner_rsa_key = None
shared_secret = None

server_keys = None

def setup():
    """Handle one-time ops with dispatch for client."""

    # post of own keys

    response = requests.post(f"http://localhost:{dispatch_port}/register_id/{self_id}")
    if response.status_code != HTTPStatus.OK:
        print(response, response.txt, file=sys.stderr)
        exit("unable to register with dispatch")
    
    dh_public = ec.export_dh_public(key_dh)
    response = requests.post(f"http://localhost:{dispatch_port}/publish_dh_key/{self_id}", data=dh_public)
    if response.status_code != HTTPStatus.OK:
        print(response, response.txt, file=sys.stderr)
        exit("unable to post dh key with dispatch")

    rsa_public = ec.export_rsa_public(key_rsa)
    response = requests.post(f"http://localhost:{dispatch_port}/publish_rsa_key/{self_id}", data=rsa_public)
    if response.status_code != HTTPStatus.OK:
        print(response, response.txt, file=sys.stderr)
        exit("unable to post rsa key with dispatch")

    print(f"Completed posting id:{self_id}.")
    time.sleep(1)

    # get of partner's keys

    response = requests.get(f"http://localhost:{dispatch_port}/retrieve_dh_key/{partner_id}")
    while response.status_code != HTTPStatus.OK:
        time.sleep(2)
        print(f"Waiting for availability of partner_id:{partner_id} dh key.")
        response = requests.get(f"http://localhost:{dispatch_port}/retrieve_dh_key/{partner_id}")

    partner_dh_key = response.content
    shared_secret = ec.generate_dh_shared_secret(key_dh, partner_dh_key) # store shared

    response = requests.get(f"http://localhost:{dispatch_port}/retrieve_rsa_key/{partner_id}")
    while response.status_code != HTTPStatus.OK:
        time.sleep(2)
        print(f"Waiting for availability of partner_id:{partner_id} rsa key.")
        response = requests.get(f"http://localhost:{dispatch_port}/retrieve_rsa_key/{partner_id}")

    print(f"Collected partner:{partner_id} keys.")


def message_loop():
    while True:
        curr_round = requests.get("http://localhost:5001/current_round").text
        message = input(f"ID:{self_id} Round:{curr_round} Message $> ")
        
        packet = Packet()

        send_addr = deaddrop_address(shared_secret, self_id, partner_id, curr_round)
        recv_addr = deaddrop_address(shared_secret, partner_id, self_id, curr_round)
 
        # conversant
        payload = pl.Payload(send_addr, recv_addr, message.ljust(512).encode())
            
        packet.payload = pl.export_payload(payload)


        with open("server_keys.json") as f:
            keys = [k.encode() for k in json.loads(f.read())]

        packet.client_prep_up(keys)

        requests.post(f"http://localhost:{5001}/submission/{self_id}", data=packet.send_out())

        # busy wait

        response = requests.get(f"http://localhost:5001/deaddrop/{self_id}")

        while response.status_code != HTTPStatus.OK:
            time.sleep(4)
            print("waiting for server")
            response = requests.get(f"http://localhost:5001/deaddrop/{self_id}")

        packet.client_prep_down(response.content)

        print(f"[{time.strftime('%a %H:%M:%S')}] {packet.send_out().decode().strip()}")
    
def deaddrop_address(shared, sender_id, recipient_id, round):
    """
    Generate the deaddrops for this round.
    TODO: Make better
    """
    start = sender_id + recipient_id 

    return start.ljust(256).encode()

if __name__ == "__main__":
    dispatch_port = sys.argv[1]
    server_port = sys.argv[2]

    self_id = sys.argv[3]
    partner_id = sys.argv[4]

    key_rsa = ec.generate_rsa()
    DH_key = ec.generate_dh()

    setup()
    message_loop()
