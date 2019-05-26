#! /usr/bin/env python3

# server.py
# state interface class for server: implemented as webserver process state,
# could be attached to database for RESTful

import os, sys, io, json, random
from enum import Enum

sys.path.append(os.path.abspath('../Kudu'))

import lib.easy_crypto as ec

class Server:
    class Modes(Enum):
        RECEIVING = 1
        PROCESSING = 2
        DISTRIBUTING = 3

    def __init__(self, client_count=0, server_count=3):
        self.client_count = client_count
        self._rsa_key = ec.generate_rsa()

        self.current_round = 0
        self.mode = Server.Modes.RECEIVING

        self.deaddrops = {}
        self.packets = set()

        self.bundle = None

        

    def reset(self):
        if self.mode != Server.Modes.DISTRIBUTING:
            raise ValueError("not ready to reset")

        self.current_round += 1
        self.mode = Server.Modes.RECEIVING

        self.deaddrops = {}
        self.packets = set()

        self.bundle = None

    # handles
    def collect_request(self, id, data):
        if self.mode != Server.Modes.RECEIVING:
            raise ValueError("not ready to receive")

        self.packets.add(Packet(data=data, origin=True, caller_id=id))

        # if all expected are received, process them in
        if len(self.packets) == self.client_count:
            self.mode = Server.Modes.PROCESSING
            self.process_requests()


    def process_requests(self):
        if self.mode != Server.Modes.PROCESSING:
            raise ValueError("not ready to process")
        elif self.bundle:
            raise ValueError("not ready to process")

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

    def get_public_key(self):
        """Returns this server's public RSA key."""
        return ec.export_rsa_public(self._rsa_key)

class Packet:
    def __init__(self):
        # raw data recieved for processing; initial
        self._inbox = None
        # processed data to be sent onward
        self._outbox = None

        # the key to be collected on pass-up and used on the pass-down
        self._symm_key = None

        # if a packet is created for dummy/statistical noise ops
        self.noise = False


    def load_up(self, data):
        if not isinstance(data, bytes):
            raise ValueError("data is invalid type")
        elif self._symm_key:
            raise ValueError("symm_key loaded; up already run")
        elif self._inbox:
            raise ValueError("already loaded")
        self._inbox = data
    
    def load_down(self, data):
        if not isinstance(data, bytes):
            raise ValueError("data is invalid type")
        elif not self._symm_key:
            raise ValueError("symm_key missing")
        elif self._inbox:
            raise ValueError("already loaded")
        self._inbox = data


    def load_noise(self, size):
        self.noise = True
        # TODO: generate noise
        raise NotImplementedError("not noise compatible")

    def onion_peel_layer(self, private_key):
        """
        Strips layer of encryption from inbox data using private_key param.
        Preserves the nested symm_key and message payload; clears inbox.
        Stores results in outbox.
        """
        if not isinstance(private_key, bytes):
            raise ValueError("key is missing or invalid type")
        elif not (self._inbox and isinstance(self._inbox, bytes)):
            raise ValueError("_inbox is missing or invalid type")
        elif self._symm_key or self._outbox:
            raise ValueError("symm_key and/or outbox filled; already peeled")

        peeled = ec.decrypt_rsa(self._inbox, private_key)
        self._inbox = None

        string_in = io.BytesIO(peeled) # process peeled string as file
        self._symm_key, self._outbox = [ string_in.read(x) for x in (ec.AES_SIZE, -1) ]

    def onion_add_layer(self):
        """
        Adds layer of encryption to inbox data using stroed symm_key field.
        Clears the nested symm_key and inbox data.
        Stores results in outbox.
        """
        if not self._inbox:
            raise ValueError("missing inbox for decrypt")
        if self._outbox:
            raise ValueError("already value in outbox")
        elif not (self._symm_key and isinstance(self._symm_key, bytes)):
            raise ValueError("invalid symm_key byte string")

        self._outbox = ec.encrypt_aes(self._inbox, self._symm_key)
        self._inbox = None
        self._symm_key = None

    def send_out(self):
        """
        Returns and clears outbox field.
        Clears outbox field to wait on upstream response.
        """
        if self._inbox or not self._outbox:
            raise ValueError(f"Illegal state in packet: '{[v for v in vars(self) if v]}' have values")

        out_bound = self._outbox
        self._outbox = None
        return out_bound



# server/bundle.py
# A representation of inter-server communication: Namely, the list of operable
# requests to be fulfilled for a client (a bundle of packets).
# Includes facilites for core Vuvuzela operations:
# Encryption, decryption, shuffle, and unshuffle.
class Bundle:
    def __init__(self):
        self._shuffle_key = None


    def load_up(self, raws):
        self.packets = [Packet() for _ in raws]
        for r, p in zip(raws, self.packets):
            p.load_up(r)

    def load_down(self, raws):
        for r, p in zip(raws, self.packets):
            p.load_down(r)


    def append_raw(self, raw):
        p = Packet()
        p.load_up(raw)
        self.packets.append(p)

    # Inter-server ops

    def send_up(self, private_key):
        """
        Given the servers private key, decrypts each packet.
        """
        for p in self.packets:
            p.onion_peel_layer(private_key)
        self._forward_shuffle_packets()
        
        upbound = [p.send_out() for p in self.packets]
        return upbound

    # preps for passing back down chain
    def send_down(self):
        for p in self.packets:
            p.onion_add_layer()
        self._reverse_shuffle_packets()
        
        downbound = [p.send_out() for p in self.packets]
        self.packets = []
        return downbound

    # shuffles the bundled packets using an optionally provided key
    # returns shuffle map (list of original indices)
    def _forward_shuffle_packets(self):
        if self._shuffle_key:
            raise ValueError("already shuffled")

        indexed = list(enumerate(self.packets))
        random.shuffle(indexed)

        self.packets = [packet for _, packet in indexed]
        self._shuffle_key = [i for i, _ in indexed]

    # given the key, performs the unshuffle
    def _reverse_shuffle_packets(self):
        if not self._shuffle_key:
            raise ValueError("not shuffled")

        self.packets = [packet for _, packet in \
            sorted(zip(self._shuffle_key, self.packets), key=lambda x: x[0])]
        self._shuffle_key = None
