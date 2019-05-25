# server/packet.py

import json, io
from collections import namedtuple, deque

import lib.easy_crypto as ec

Contents = namedtuple("contents", ["collect", "drop", "message"])

# wrapper for packet used in server operations
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


    def load_up(self,data=None):
        if not isinstance(data, bytes):
            raise ValueError("data is invalid type")
        elif self._symm_key:
            raise ValueError("symm_key loaded; up already run")
        elif self._inbox:
            raise ValueError("already loaded")
        self._inbox = data
    
    def load_down(self,data=None):
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