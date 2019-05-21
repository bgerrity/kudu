#! /usr/bin/env python3

# server.py
# state interface class for server: implemented as webserver process state,
# could be attached to database for RESTful

import json
from collections import namedtuple
from enum import Enum 

# from bundle import Bundle
from packet import Packet

Key_Pair = namedtuple("keys", ["public", "private"])

class Server:
    class States(Enum):
        RECEIVING = 1 
        PROCESSING = 2
        DISTRIBUTING = 3

    def __init__(self, client_count=0):
        self.current_round = -1
        # self.bundle = None
        self.client_count = client_count
        self.key_pair = Key_Pair("foo", "bar")

        self.state = Server.States.RECEIVING

        self.current_round = 0
        self.deaddrops = {}
        self.packets = {}

    # # TODO: implement
    # # indicates if server is in recieve mode
    # def accepting_requests(self):
    #     return self.receive_mode        

    def reset(self):
        self.receive_mode = True
        self.distribute_mode = False

        self.current_round += 1
        self.deaddrops = {}
        self.packets = {}

    def collect_request(self, id, packet):
        if self.state != Server.States.RECEIVING:
            raise ValueError("not ready to receive")

        self.packets[id] = packet

        # if all expected are received, process them in
        if len(self.packets.keys()) == self.client_count:
            self.state = Server.States.PROCESSING
            self.process_requests()
        
    
    def process_requests(self):
        if self.state != Server.States.PROCESSING:
            raise ValueError("not ready to process")

        # process drops in
        for id, packet in self.packets.items():
            packet.decrypt_and_process("bar")
            self.deaddrops[packet.contents.drop] = packet.contents.message
        # finished processing

    def return_request(self, id):
        if self.state != Server.States.DISTRIBUTING:
            raise ValueError("not ready to distribute")
        elif id not in self.packets:
            raise ValueError("no such id was recieved")
        
        requested_drop = self.packets[id].contents.collect
        result = self.deaddrops.pop(requested_drop)


        if len(self.deaddrops) == 0: # exit distribute mode and return to recieving
            self.reset()

        return result




