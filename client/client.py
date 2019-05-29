#! /usr/bin/env python3

from http import HTTPStatus
import requests

import os, sys, time, json

sys.path.append(os.path.abspath('../Kudu'))

import lib.easy_crypto as ec
import lib.payload as pl

from packet import Packet

dispatch_port = None

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
        exit("unable to register with dispatch")
    # print(response.text)

    
    dh_public = ec.export_dh_public(key_dh)
    response = requests.post(f"http://localhost:{dispatch_port}/publish_dh_key/{self_id}", data=dh_public)
    if response.status_code != HTTPStatus.OK:
        exit("unable to post dh key with dispatch")
    # print(response.text)

    rsa_public = ec.export_rsa_public(key_rsa)
    response = requests.post(f"http://localhost:{dispatch_port}/publish_rsa_key/{self_id}", data=rsa_public)
    if response.status_code != HTTPStatus.OK:
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
        message = input(f"ID:{self_id} Round:{partner_id} Message $> ")
        
        packet = Packet()

        send_addr = deaddrop_address(shared_secret, self_id, partner_id, curr_round)
        recv_addr = deaddrop_address(shared_secret, partner_id, self_id, curr_round)
        print("send:", send_addr)
        print("recv:", recv_addr)

 
        # conversant
        payload = pl.Payload(send_addr, recv_addr, message.ljust(512).encode())
            
        packet.payload = pl.export_payload(payload)


        with open("server_keys.json") as f:
            keys = [k.encode() for k in json.loads(f.read())]

        packet.client_prep_up(keys)

        requests.post(f"http://localhost:5001/submission/{self_id}", data=packet.send_out())

        # busy wait

        response = requests.get(f"http://localhost:5001/deaddrop/{self_id}")

        while response.status_code != HTTPStatus.OK:
            time.sleep(2)
            print("waiting for server")
            response = requests.get(f"http://localhost:5001/deaddrop/{self_id}")
            print(response)

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
    self_id = sys.argv[2]
    partner_id = sys.argv[3]

    key_rsa = ec.generate_rsa()
    DH_key = ec.generate_dh()

    setup()
    message_loop()




# class Client:
#     def __init__(self):

#     # query dispatch for its partner (may be none)
#     def get_partner_keys(self):
#         return 0 # TODO this might change

#     # query user for message to send
#     def collect_message(self):
#         raise NotImplementedError

#     # instantiate round struct
#     def create_round(self):
#         raise NotImplementedError

#     # instantiate noise message
#     def create_round_noise(self):
#         raise NotImplementedError

#     # send up to server
#     def send_round(self):
#         raise NotImplementedError

#     # collect server
#     def collect_round(self):
#         raise NotImplementedError

#     # wrappers for openssl
#     def encrypt(self):
#         raise NotImplementedError

#     def decrypt(self):
#         raise NotImplementedError


# def postKeys():
#     # posts the public RSA key to the server
#     response = requests.post('http://127.0.0.1:5000/publish_key/'+ client.id, data = client.keys[1])
#     if response.status_code == HTTPStatus.ACCEPTED:
#         print("Public Key posted")

#     # posts the diffie hellman public key to the server
#     # TODO change DH_public according to the new return value in easy_crypto
#     DH_public = str(client.DH_key.getPublicKey()).encode()
#     response2 = requests.post('http://127.0.0.1:5000/publish_DH_key/'+ client.id, data = DH_public)
#     if response2.status_code == HTTPStatus.ACCEPTED:
#         print("Public DH Key posted")

#     # when done with posting keys increments the number of users
#     response3 = requests.post('http://127.0.0.1:5000/increment_users')
#     if response3.status_code == HTTPStatus.ACCEPTED:
#         print("Client finished posting")

# def getKeys():
#     response = requests.get('http://127.0.0.1:5000/get_key/' + client.partner)
#     while(response.status_code != HTTPStatus.ACCEPTED):
#         time.sleep(1)
#         response = requests.get('http://127.0.0.1:5000/get_key/' + client.partner)

#     client.partner_key = RSA.import_key(response.content.decode())
#     print("Imported partner's key")

#     response2 = requests.get('http://127.0.0.1:5000/get_DH_key/' + client.partner)
#     while(response2.status_code != HTTPStatus.ACCEPTED):
#         time.sleep(1)
#         response2 = requests.get('http://127.0.0.1:5000/get_DH_key/' + client.partner)

#     # TODO still broken for the DH key
#     DH_pub = int(response2.content.decode())
#     client.shared_secret = client.DH_key.update(DH_pub)
#     print("Generated shared secret")
