#! /usr/bin/env python3
# client/client.py

from http import HTTPStatus
from threading import Lock

import requests

import os, sys, time, json, argparse

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

queue_lock = Lock()

def setup():
    """Handle one-time ops with dispatch for client."""

    url = f"http://localhost:{dispatch_port}/retrieve_server_keys"
    response = requests.get(url)
    if response.status_code != HTTPStatus.OK:
        print(response, response.text, file=sys.stderr)
        exit("unable to collect server keys from dispatch")

    global server_keys
    server_keys = [k.encode() for k in json.loads(response.content)]

    # post own keys

    url = f"http://localhost:{dispatch_port}/register_id/{self_id}"
    response = requests.post(url)
    if response.status_code != HTTPStatus.OK:
        print(response, response.text, file=sys.stderr)
        exit("unable to register with dispatch")
    
    dh_public = ec.export_dh_public(key_dh)
    url = f"http://localhost:{dispatch_port}/publish_dh_key/{self_id}"
    response = requests.post(url, data=dh_public)
    if response.status_code != HTTPStatus.OK:
        print(response, response.text, file=sys.stderr)
        exit("unable to post dh key with dispatch")

    rsa_public = ec.export_rsa_public(key_rsa)
    url = f"http://localhost:{dispatch_port}/publish_rsa_key/{self_id}"
    response = requests.post(url, data=rsa_public)
    if response.status_code != HTTPStatus.OK:
        print(response, response.text, file=sys.stderr)
        exit("unable to post rsa key with dispatch")

    print(f"Completed posting id:{self_id}.")
    time.sleep(1)

    # get partner's keys

    url = f"http://localhost:{dispatch_port}/retrieve_dh_key/{partner_id}"
    response = requests.get(url)
    while response.status_code != HTTPStatus.OK:
        time.sleep(2)
        print(f"Waiting for availability of partner_id:{partner_id} dh key.")
        response = requests.get(url)

    partner_dh_key = response.content
    shared_secret = ec.generate_dh_shared_secret(key_dh, partner_dh_key) # store shared

    response = requests.get(url)
    url = f"http://localhost:{dispatch_port}/retrieve_rsa_key/{partner_id}"
    while response.status_code != HTTPStatus.OK:
        time.sleep(2)
        print(f"Waiting for availability of partner_id:{partner_id} rsa key.")
        response = requests.get(url)

    print(f"Collected partner:{partner_id} keys.")


def message_loop():
    url = f"http://localhost:{server_port}/current_round"
    curr_round = int(requests.get(url).text)

    while True:
        message = None
        while not message: # prompt until valid message
            clear_send = input(f"ID:{self_id} Round:{curr_round} Message $> ")
            try:
                message = pl.construct_message(clear_send)
            except (TypeError, ValueError, UnicodeEncodeError) as e:
                message = None
                print("Message invalid:", e)
        
        packet = Packet()

        send_addr = deaddrop_address(shared_secret, self_id, partner_id, curr_round) # drop
        recv_addr = deaddrop_address(shared_secret, partner_id, self_id, curr_round) # collect
 
        # conversant
        payload = pl.Payload(send_addr, recv_addr, message)
            
        packet.payload = pl.export_payload(payload)

        packet.client_prep_up(server_keys)

        # send out message
        url = f"http://localhost:{server_port}/submission/{self_id}"
        requests.post(url, data=packet.send_out())

        # wait on response
        url = f"http://localhost:{server_port}/deaddrop/{self_id}"
        response = requests.get(url)
        while response.status_code != HTTPStatus.OK:
            time.sleep(4)
            print("waiting for server")
            response = requests.get(url)

        packet.client_prep_down(response.content)

        try:
            message_recieved = pl.deconstruct_message(packet.send_out())
        except (TypeError, ValueError, UnicodeDecodeError) as e:
            message_recieved = f"RECEIVED INVALID: {e}"

        print(f"[{time.strftime('%a %H:%M:%S')}]", message_recieved)

        curr_round += 1
    
def deaddrop_address(shared, sender_id, recipient_id, round):
    """
    Generate the deaddrops for this round.
    TODO: Make better -- actually hashing using shared etc
        Use pl.ADDRESS_SIZE for address sizing
    """
    start = sender_id + recipient_id 

    return start.ljust(256).encode()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Launch a client.')
    parser.add_argument("self_id", help="the id for this client")
    parser.add_argument("partner_id", help="the id for its conversation partner")
    parser.add_argument("-d", "--dispatch-port", nargs=1, type=int, default=5000,
        help="the port for the dispatch server")
    parser.add_argument("-s", "--server-port", nargs=1, type=int, default=5001,
        help="the port for the Vuvuzela server")

    args = parser.parse_args()

    dispatch_port = args.dispatch_port
    server_port = args.server_port

    self_id = args.self_id
    partner_id = args.partner_id

    key_rsa = ec.generate_rsa()
    key_dh = ec.generate_dh()

    setup()
    message_loop()
