#! /usr/bin/env python3

import subprocess, time, os, sys

sys.path.append(os.path.abspath('../kudu'))


def spin_up_dispatch_server():
    subprocess.call(["gnome-terminal", "--", "dispatch/dispatch.py", "2"])
    time.sleep(1)

def spin_up_clients():
    subprocess.call(["gnome-terminal", "--", "client/client.py", "1", "2"])
    subprocess.call(["gnome-terminal", "--", "client/client.py", "2", "1"])
    print("started clients")

def spin_up_vuvuzela_server():
    subprocess.call(["gnome-terminal", "--", "server/app.py", "2"])
    time.sleep(5)

spin_up_dispatch_server()
spin_up_vuvuzela_server()
spin_up_clients()
