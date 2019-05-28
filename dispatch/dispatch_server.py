#! /usr/bin/env python3

#
# Serves as CDN analogue for dialing.
# As the dialing protocol is unimplemented, for demonstration purposes, handles the distribution of
# public keys to clients.
#
# For demonstration, used to bootstrap server and client processes.
# Also provides standardization info to partipating processes (i.e. constraints and protocol specifications).
#
# README: Must be trusted for all purposes but CDN as Kudu lacks full implmentation.
# . venv/bin/activate

from flask import Flask, Response, request, redirect, jsonify
import subprocess
import time
import sys
from http import HTTPStatus
from threading import Lock

class Dispatch:
    def __init__(self):
        self.num_clients = 0
        # dictionary that will hold all public keys
        self.public_keys = {}
        self.DH_pub_keys = {}

app = Flask(__name__)
keys = Dispatch()
server_lock = Lock() # general purpose lock

@app.route("/increment_users", methods=['POST'])
def increment_users():
    keys.num_clients = keys.num_clients + 1

    return f"incremented", HTTPStatus.ACCEPTED

@app.route("/publish_DH_key/<int:id>", methods=['POST'])
def publish_DH_key(id):
    key = request.data
    with server_lock:
        keys.DH_pub_keys[id] = key

    return f"Received DH key from {id}", HTTPStatus.ACCEPTED

@app.route("/get_DH_key/<int:id>", methods=["GET"])
def get_DH_key(id):
    if keys.num_clients != 2:
        return f"Wait", HTTPStatus.PROCESSING

    try:
        partner_key = keys.DH_pub_keys[id]
    except KeyError:
        return f"No_Key", HTTPStatus.BAD_REQUEST

    return f"{partner_key}", HTTPStatus.ACCEPTED

# dispatch server port
@app.route("/dispatch_port", methods=['GET'])
def get_port():
    return f"5000", HTTPStatus.ACCEPTED

# vuvuzela server port
@app.route("/server_port", methods=['GET'])
def get_servr_port():
    return f"5001", HTTPStatus.ACCEPTED

# id will be the id that a client will hold
# so when making a call to this the client will give it's id and public key
@app.route("/publish_key/<int:id>", methods=['POST'])
def publish_key(id):
    key = request.data
    with server_lock:
        keys.public_keys[id] = key

    return f"Received key from {id}", HTTPStatus.ACCEPTED

@app.route("/get_key/<int:id>", methods=['GET'])
def get_key(id):
    if keys.num_clients != 2:
        return f"Wait", HTTPStatus.PROCESSING

    try:
        partner_key = keys.public_keys[id]
    except KeyError:
        return f"No_Key", HTTPStatus.BAD_REQUEST

    return f"{partner_key}", HTTPStatus.ACCEPTED

if __name__ == '__main__':
    port = 5000
    app.run(debug=True, port=port)
