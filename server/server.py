#! /usr/bin/env python3
# server/server.py

# server.py
# state interface class for server: implemented as webserver process state
# hosts server's business logic; could be attached to database for RESTful api

import os, sys, io, json, random
from enum import Enum
from collections import OrderedDict

sys.path.append(os.path.abspath('../Kudu'))

import lib.easy_crypto as ec
import lib.payload as pl

class Server:
    class Modes(Enum):
        RECEIVING = 1
        PROCESSING = 2
        DISTRIBUTING = 3

    def __init__(self, client_count=2, server_count=5):
        self.CLIENT_COUNT = client_count
        self.SERVER_COUNT = server_count

        # vector of server keys
        self._keys = [ec.generate_rsa() for _ in range(self.SERVER_COUNT)]
        with open("server_keys.json", "w") as f: # export keys for use by clients (test without dispatch) TODO: remove on merge with dispatch branch
            f.write(json.dumps(self._get_privates()))

        self.current_round = 0
        self.mode = Server.Modes.RECEIVING

        self._id_map = OrderedDict() # {id: data}
        self._responses = None # {id: deaddrop_result}

        # TODO: refactor out
        self._bundles = None # representation of each servers internal state

    def _get_privates(self):
        return [ec.export_rsa_public(k).decode() for k in self._keys]

    def reset(self):
        if self.mode != Server.Modes.DISTRIBUTING:
            raise ValueError("not ready to reset")

        self.current_round += 1
        self.mode = Server.Modes.RECEIVING

        self._id_map = OrderedDict()
        self._responses = None

        self._bundles = None # regenerate each round

    # handles
    def collect_request(self, id, data):
        if self.mode != Server.Modes.RECEIVING:
            raise ValueError("not ready to receive")
        elif id in self._id_map:
            raise ValueError(f"already recieved a submission this round by id:{id}")

        self._id_map[id] = data

        # if all expected are received, process them in
        if len(self._id_map) == self.CLIENT_COUNT:
            self.mode = Server.Modes.PROCESSING
            self._process_requests()


    def _process_requests(self):
        if self.mode != Server.Modes.PROCESSING:
            raise ValueError(f"not ready to process: in state {self.mode}")
        elif self._bundles:
            raise ValueError("bundles already exist; can't process")

        self._bundles = [Bundle() for _ in range(self.SERVER_COUNT)]

        rsa_priv_keys = [k.export_key() for k in self._keys]

        # sequentially process up
        prev_up = list(self._id_map.values()) # initial is direct from client: final is terminal's decrypted
        for b, pk in zip(self._bundles, rsa_priv_keys):
            b.load_up(prev_up)
            prev_up = b.send_up(pk)

        terminal_raws = prev_up

        prev_down = self._terminal_process(terminal_raws)

        for b in reversed(self._bundles): # go in the opposite direction now
            b.load_down(prev_down)
            prev_down = b.send_down()
        
        self._responses = {id: resp for id, resp in zip(self._id_map.keys(), prev_down)}

        self.mode = Server.Modes.DISTRIBUTING

    # given the raw decrypts, runs the deaddrops
    def _terminal_process(self, raws):
        processed = []

        # process each
        for r in raws:
            try:
                contents = pl.import_payload(r)
            except KeyError: # invalid upload
                contents = None
            
            processed.append(contents)

        deaddrops = {}

        # fill deaddrops
        for p in processed:
            if p:
                deaddrops[p.drop] = p.message

        results = []
        # now collect from them
        for p in processed:
            try:
                collected = deaddrops[p.collect] if p else None 
            except KeyError:
                collected = "INVALID_REQUEST".encode()          
            results.append(collected)

        # TODO: handle invalids betters

        return results
        

    def return_request(self, id):
        if self.mode != Server.Modes.DISTRIBUTING:
            raise ValueError("not ready to distribute")
        elif id not in self._id_map:
            raise ValueError(f"no such id:{id} was received")

        result = self._responses.pop(id)

        if len(self._responses) == 0: # exit distribute mode and return to recieving
            self.reset()

        return result

    # def get_public_key(self):
    #     """Returns this server's public RSA key."""
    #     return ec.export_rsa_public(self._rsa_key)

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
