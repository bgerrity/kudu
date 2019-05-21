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

import subprocess

# launch the server and a client
subprocess.call(["gnome-terminal", "--", "server/app.py"])
subprocess.call(["gnome-terminal", "--", "./client.py"])

class Dispatch:
    None
    # TODO: define const table
    # message size
    # deadrop slot count (and ranges)
    # deadrop index format
    # padding rules
