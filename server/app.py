#! /usr/bin/env python3
# server/app.py

import argparse, json

from flask import Flask, Response, request
import requests

from sys import argv
from http import HTTPStatus
from threading import Lock

from server import Server # hacky.db interface

app = Flask(__name__)

dispatch_port = None
client_count = None

server_lock = Lock() # general purpose lock

db = None

@app.route("/")
def hello():
    return "Hello from the server!"

# stores uploaded packet
@app.route('/submission/<int:id>', methods=['POST'])
def post_submission(id):
    with server_lock:
        if db.mode == db.Modes.RECEIVING:
            db.collect_request(id, request.data)
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
        elif id not in db._id_map:
            return f"No request by id:{id}", HTTPStatus.BAD_REQUEST

        try:
            response = collect_drop(id)
        except KeyError:
            return f"Already returned id:{id}", HTTPStatus.BAD_REQUEST


    return Response(response)

# given an id, services its requested drop
# assumes server lock is owned by thread
def collect_drop(id):
    return db.return_request(id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch the Vuvuzela server.')
    parser.add_argument("client_count", type=int, help="the number of clients")
    parser.add_argument("-d", "--dispatch-port", type=int, default=5000,
        help="the port for the dispatch server")
    parser.add_argument("-s", "--server-port", type=int, default=5001,
        help="the port for this Vuvuzela server")

    args = parser.parse_args()

    client_count = args.client_count
    port = args.server_port
    dispatch_port = args.dispatch_port

    db = Server(client_count) # state manager

    # publish keys to dispatch for use by clients

    key_data = json.dumps(db.get_public_keys())
    url = f"http://localhost:{dispatch_port}/publish_server_keys"
    response = requests.post(url, data=key_data)
    if response.status_code != HTTPStatus.OK:
        print(response, response.text)
        exit("server unable to publish keys to dispatch")

    app.run(debug=True, port=port)
