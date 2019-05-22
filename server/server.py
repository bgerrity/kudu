#! /usr/bin/env python3

# server.py
# state interface class for server: implemented as webserver process state,
# could be attached to database for RESTful

import json
from collections import namedtuple
from enum import Enum

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# from bundle import Bundle
from packet import Packet

Key_Pair = namedtuple("keys", ["public", "private"])

class Server:
    class Modes(Enum):
        RECEIVING = 1
        PROCESSING = 2
        DISTRIBUTING = 3

    def __init__(self, client_count=0):
        self.client_count = client_count
        self.key_pair = Server.gen_key_pair()

        self.current_round = 0
        self.mode = Server.Modes.RECEIVING

        self.deaddrops = {}
        self.packets = {}

    @staticmethod
    def gen_key_pair():
        # TODO: return to generation when dispathc enabled
        with open("server/fixed-key.pem", "rb") as f:
            server_key = RSA.import_key(f.read())
        # server_key = RSA.generate(2048)
        return Key_Pair(server_key.publickey().export_key(), server_key.export_key())

    def reset(self):
        self.current_round += 1
        self.deaddrops = {}
        self.packets = {}
        self.mode = Server.Modes.RECEIVING

    # handles
    def collect_request(self, id, packet):
        if self.mode != Server.Modes.RECEIVING:
            raise ValueError("not ready to receive")

        self.packets[id] = packet

        # if all expected are received, process them in
        if len(self.packets.keys()) == self.client_count:
            self.mode = Server.Modes.PROCESSING
            self.process_requests()


    def process_requests(self):
        if self.mode != Server.Modes.PROCESSING:
            raise ValueError("not ready to process")

        # process drops in
        for _, packet in self.packets.items():
            packet.decrypt_and_process(self.key_pair.private)
            self.deaddrops[packet.contents.drop] = packet.contents.message

        self.mode = Server.Modes.DISTRIBUTING

    def return_request(self, id):
        if self.mode != Server.Modes.DISTRIBUTING:
            raise ValueError("not ready to distribute")
        elif id not in self.packets:
            raise ValueError("no such id was received")

        requested_drop = self.packets[id].contents.collect
        result = self.deaddrops.pop(requested_drop)


        if len(self.deaddrops) == 0: # exit distribute mode and return to recieving
            self.reset()

        return result
