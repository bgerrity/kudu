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

# launch the server and a clients

app = Flask(__name__)

class Dispatch:
    None
    # TODO: define const table
    # message size
    # deadrop slot count (and ranges)
    # deadrop index format
    # padding rules

@app.route("/dispatch_port", methods=['GET'])
def get_port():
    return 5000


if __name__ == '__main__':
    port = 5000
    app.run(debug=True, port=port)
