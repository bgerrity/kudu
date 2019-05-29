#! /usr/bin/env python3
# server/dispatch_server.py

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
import sys, time
from sys import argv
from http import HTTPStatus
from threading import Lock


app = Flask(__name__)

expected_clients = None
server_port = None # the

server_lock = Lock() # general purpose lock

# id of users -- required before any other operations
registered_ids = set()

# public keys of clients
public_keys_rsa = {}
public_keys_dh = {}

@app.route("/register_id/<int:id>", methods=['POST'])
def register_id(id):
    with server_lock:
        if len(registered_ids) >= expected_clients:
            return f"registered id count cap:{expected_clients} reached", HTTPStatus.CONFLICT
        if id in registered_ids:
            return f"id:{id} already registered", HTTPStatus.CONFLICT

        registered_ids.add(id)

    return f"registered id:{id} ({len(registered_ids)} for {expected_clients})"

@app.route("/registered/", methods=['GET'])
def registered():
    with server_lock:
        return jsonify(list(registered_ids))

@app.route("/publish_dh_key/<int:id>", methods=['POST'])
def publish_dh_key(id):
    with server_lock:
        if id not in registered_ids:
            return f"id:{id} not registered", HTTPStatus.CONFLICT
        if id in public_keys_dh:
            return f"id:{id} already published dh key", HTTPStatus.CONFLICT

        key = request.data
        public_keys_dh[id] = key

    return f"received DH key from id:{id}"

@app.route("/retrieve_dh_key/<int:id>", methods=['GET'])
def retrieve_dh_key(id):
    with server_lock:
        if id not in registered_ids:
            return f"id:{id} not registered", HTTPStatus.NOT_FOUND
        if id not in public_keys_dh:
            return f"id:{id} registered but dh key not available", HTTPStatus.NOT_FOUND

        key = public_keys_dh[id]

    return key

@app.route("/publish_rsa_key/<int:id>", methods=['POST'])
def publish_rsa_key(id):
    with server_lock:
        if id not in registered_ids:
            return f"id:{id} not registered", HTTPStatus.CONFLICT
        if id in public_keys_rsa:
            return f"id:{id} already published rsa key", HTTPStatus.CONFLICT

        key = request.data
        public_keys_rsa[id] = key

    return f"received RSA key from id:{id}"

@app.route("/retrieve_rsa_key/<int:id>", methods=['GET'])
def retrieve_rsa_key(id):
    with server_lock:
        if id not in registered_ids:
            return f"id:{id} not registered", HTTPStatus.NOT_FOUND
        if id not in public_keys_rsa:
            return f"id:{id} registered but rsa key not available", HTTPStatus.NOT_FOUND

        key = public_keys_rsa[id]

    return key

@app.route("/get_server_port", methods=['GET'])
def get_server_port():
    return server_port

if __name__ == '__main__':
    port = 5000
    server_port = 5001
    expected_clients = 2

    try:
        port = int(argv[1])
    except (ValueError, IndexError):
        pass
    try:
        server_port = int(argv[2])
    except (ValueError, IndexError):
        pass
    try:
        client_count = int(argv[3])
    except (ValueError, IndexError):
        pass
    try:
        expected_clients = int(argv[4])
    except (ValueError, IndexError):
        pass

    app.run(debug=True, port=port)

