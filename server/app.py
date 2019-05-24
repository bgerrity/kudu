#! /usr/bin/env python3

# app.py

from flask import Flask, Response, request, redirect, jsonify

from sys import argv
from http import HTTPStatus
from collections import deque
from threading import Lock

from server import Server # hacky.db interface
from packet import Packet

app = Flask(__name__)

dispatch_port = None

server_lock = Lock() # general purpose lock

db = Server(2)

# holds the tuples of the server chain crypt keys (public, private)
# ordered from origin to deaddrop (TODO: bettter phrasing?)
chain_keys = [("foo", "bar"), ("titi", "toto"), ("biz", "baz")]

@app.route("/")
def hello():
    return "Hello from the server!"

# stores uploaded packet
@app.route('/submission/<int:id>', methods=['POST'])
def post_submission(id):
    packet = Packet(request.data, terminal=True)

    with server_lock:
        if db.mode == db.Modes.RECEIVING:
            db.collect_request(id, packet)
        else:
            return f"Server not receiving", HTTPStatus.BAD_REQUEST

    return f"Received POST from {id}", HTTPStatus.ACCEPTED

@app.route('/current_round', methods=['GET'])
def get_current_round():
    with server_lock:
        round = db.current_round
    return f"{round}", HTTPStatus.OK

@app.route('/deaddrop/<int:id>', methods=['GET'])
def get_response(id):
    with server_lock:
        if db.mode != db.Modes.DISTRIBUTING:
            return "Server not distributing", HTTPStatus.BAD_REQUEST
        elif id not in db.packets:
            return f"No request by id:{id}", HTTPStatus.BAD_REQUEST

        try:
            response = {
                "round": db.current_round,
                "collected": collect_drop(id)
            }
        except KeyError:
            return f"Already returned id:{id}", HTTPStatus.BAD_REQUEST

<<<<<<< HEAD
=======

>>>>>>> 3b1978e87cd20035740baa7a422c13f93bacc370
    return jsonify(response)

# given an id, services its requested drop
# assumes server lock is owned by thread
def collect_drop(id):
    return db.return_request(id)

if __name__ == '__main__':
    port = 5001
    dispatch_port = 5000

    try:
        port = int(argv[1])
    except (ValueError, IndexError):
        pass
    try:
        dispatch_port = int(argv[2])
    except (ValueError, IndexError):
        pass

    app.run(debug=True, port=port)
