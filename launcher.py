#! /usr/bin/env python3

import subprocess, time, os, sys

sys.path.append(os.path.abspath('../Kudu'))


def spin_up_dispatch_server():
    subprocess.call(["gnome-terminal", "--", "dispatch/dispatch_server.py"])
    time.sleep(2)

def spin_up_clients():
    subprocess.call(["gnome-terminal", "--", "client/client.py", "1", "2"])
    subprocess.call(["gnome-terminal", "--", "client/client.py", "2", "1"])
    print("started clients")

def spin_up_vuvuzela_server():
    subprocess.call(["gnome-terminal", "--", "server/server.py"])

spin_up_dispatch_server()
spin_up_clients()
#spin_up_vuvuzela_server()
