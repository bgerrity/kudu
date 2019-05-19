#! /usr/bin/env python3

# app.py

from flask import Flask, Response, request, redirect, jsonify
from http import HTTPStatus
import sys
from packet import Packet

app = Flask(__name__)

# hacky.db
round_packets = {} # (id: request)
deaddrops = {}

clients = {} # TODO: fill via http query to dispatch

# holds the tuples of the server chain crypt keys (public, private)
# ordered from origin to deaddrop (TODO: bettter phrasing?)
chain_keys = [("foo", "bar"), ("titi", "toto"), ("biz", "baz")]

# holds the seed used to shuffle  
reorder = None

@app.route("/")
def hello():
    return "Hello from the server!"

@app.route('/submission/<int:id>', methods=['POST'])
def post_submission(id):
    packet = Packet(request.get_json(), True)
    packet.decrypt("foo")

    try:
        packet.unwrap()
    except ValueError as e:
        return f"Incomplete submission: {e}", HTTPStatus.BAD_REQUEST
    
    round_packets[id] = packet
    process(packet)

    # # TODO: add validation to each
    # collect, message, drop = recieved.get("collect"), recieved.get("message"), recieved.get("drop")
    # if not (collect and message and drop):
    #     results = {
    #         "collect": collect, # key for requested deaddrop access
    #         "drop": drop, # key for requested deaddrop deposit
    #         "message": message, # message to be deposited
    #     }
    #     return jsonify("Incomplete submission", results), HTTPStatus.BAD_REQUEST

    return redirect(f"/deaddrop/{id}")

def process(packet):
    deaddrops[packet.drop] = packet.message

@app.route('/deaddrop/<int:id>', methods=['GET'])
def get_round(id):
    assert(id in round_packets)
    response = { 
        "collected": deaddrops.get(round_packets[id].collect)
    }

    return jsonify(response)

# if the current round is complete 
def all_recieved():
    raise NotImplementedError()

if __name__ == '__main__':
    port = 5001
    try:
        port = int(sys.argv[1])
    except (ValueError, IndexError):
        pass
    app.run(debug=True, port=port)
