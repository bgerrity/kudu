#! /usr/bin/env python3

# app.py

from flask import Flask, Response, request, redirect, jsonify
from http import HTTPStatus
import sys

app = Flask(__name__)

round_packages = {} # lookup for current round info: temporary DB. TODO: mySQL?
clients = {} # TODO: fill via http query to dispatch

@app.route("/")
def hello():
    return "Hello from the server!"

@app.route('/submission/<int:id>', methods=['POST'])
def post_submission(id):
    recieved = request.get_json()

    # TODO: add validation to each
    collect, message, drop = recieved.get("collect"), recieved.get("message"), recieved.get("drop")
    if not (collect and message and drop):
        results = {
            "collect": collect, # key for requested deaddrop access
            "drop": drop, # key for requested deaddrop deposit
            "message": message, # message to be deposited
        }
        return jsonify("Incomplete submission", results), HTTPStatus.BAD_REQUEST

    round_packages[id] = message
    return redirect(f"/deaddrop/{id}")

@app.route('/deaddrop/<int:id>', methods=['GET'])
def get_round(id):
    response = { 
        "id": id,
        "message": round_packages.get(id),
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
