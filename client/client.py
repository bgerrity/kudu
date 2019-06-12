#! /usr/bin/env python3
# client/client.py

from http import HTTPStatus
from threading import Lock

import requests

import os, sys, time, json, argparse

sys.path.append(os.path.abspath('../kudu'))

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
    global shared_secret
    shared_secret = ec.generate_dh_shared_secret(key_dh, partner_dh_key) # store shared

    url = f"http://localhost:{dispatch_port}/retrieve_rsa_key/{partner_id}"
    response = requests.get(url)
    while response.status_code != HTTPStatus.OK:
        time.sleep(2)
        print(f"Waiting for availability of partner_id:{partner_id} rsa key.")
        response = requests.get(url)

    global partner_rsa_key
    partner_rsa_key = response.content

    print(f"Collected partner:{partner_id} keys.")


def message_loop():
    url = f"http://localhost:{server_port}/current_round"
    curr_round = int(requests.get(url).text)

    while True:
        message = None
        while not message: # prompt until valid message
            clear_send = input(f"ID:{self_id} Round:{curr_round} Message $> ")
            try:
                if clear_send:
                    message = pl.construct_message(clear_send, partner_rsa_key)
                else:
                    message = pl.construct_noise(partner_rsa_key)
            except (TypeError, ValueError, UnicodeEncodeError) as e:
                print("Message invalid:", e)

        packet = Packet()

        send_addr = ec.generate_deaddrop_id(shared_secret, self_id, partner_id, curr_round) # drop
        recv_addr = ec.generate_deaddrop_id(shared_secret, partner_id, self_id, curr_round) # collect

        # conversant
        payload = pl.Payload(send_addr, recv_addr, message)

        packet.payload = pl.export_payload(payload)

        packet.client_prep_up(server_keys)

        # send out message
        url = f"http://localhost:{server_port}/submission/{self_id}"
        response = requests.post(url, data=packet.send_out())
        while response.status_code != HTTPStatus.ACCEPTED:
            time.sleep(4)
            print("waiting for server: send")
            response = requests.post(url, data=packet.send_out())


        # wait on response
        url = f"http://localhost:{server_port}/deaddrop/{self_id}"
        response = requests.get(url)
        while response.status_code != HTTPStatus.OK:
            time.sleep(4)
            print("waiting for server: return")
            response = requests.get(url)

        packet.client_prep_down(response.content)


        try:
            noise, message_recieved = pl.deconstruct_message(packet.send_out(), ec.export_rsa_private(key_rsa))

        except (TypeError, ValueError, UnicodeDecodeError) as e:
            print(f"[{time.strftime('%a %H:%M:%S')}]", f"{{Error Message Invalid: {e}}}")
        else:
            if noise:
                print(f"[{time.strftime('%a %H:%M:%S')}]", "{No Message}")
            else:
                print(f"[{time.strftime('%a %H:%M:%S')}]", message_recieved, f"{{{len(message_recieved)}}}")

        curr_round += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Launch a client.')
    parser.add_argument("self_id", help="the id for this client")
    parser.add_argument("partner_id", help="the id for its conversation partner")
    parser.add_argument("-d", "--dispatch-port", type=int, default=5000,
        help="the port for the dispatch server")
    parser.add_argument("-s", "--server-port", type=int, default=5001,
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
