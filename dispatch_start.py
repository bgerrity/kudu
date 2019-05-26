#! /usr/bin/env python3

import subprocess
import time
import sys

def spin_up_dispatch_server():
    subprocess.call(["gnome-terminal", "--", "./dispatch_server.py"])
    time.sleep(2)

def spin_up_clients():
    subprocess.call(["gnome-terminal", "--", "./client.py", "1", "2"])
    subprocess.call(["gnome-terminal", "--", "./client.py", "2", "1"])
    print("started clients")

spin_up_dispatch_server()
spin_up_clients()
#spin_up_vuvuzela_server()
