import subprocess
import time
import sys

# starts up the necessary processes

def spin_up_vuvuzela_server():
    subprocess.call(["gnome-terminal", "--", "server/app.py"])
    #time.sleep(3) # give time for server to start

def spin_up_dispatch_server():
    subprocess.call(["gnome-terminal", "--", "./dispatch_server.py"])

def spin_up_clients():
    #print("called")
    subprocess.call(["gnome-terminal", "--", "./client.py"])


spin_up_clients()
spin_up_dispatch_server()
spin_up_vuvuzela_server()
