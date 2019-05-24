# packet.py


import json, io
from collections import namedtuple, deque

import lib.easy_crypto as ec

Contents = namedtuple("contents", ["collect", "drop", "message"])

# wrapper and validator of
class Packet:
    size = None # standardized size for packets

    def __init__(self, data=None, noise=False, origin=False, terminal=False, caller_id=None, client=False):
        # raw data recieved for processing; initial
        self.data = data

        # the key or vector of keys to be used to encrypt (by server) or decrypt (by client)
        self.symm_keys = None
        # binary string prior to encryption or decryption to be sent onward
        self.payload = None

        self.origin = origin
        self.terminal = terminal
        self.client = client
        if self.client:
            if self.origin or self.terminal:
                raise NotImplementedError("cannot be client and origin/terminal")
        # else: # am server
        #     if not self.origin:
        #         raise NotImplementedError("no inter-server support")
        #     elif not self.terminal:
        #         raise NotImplementedError("no inter-server support")

        if caller_id and noise:
            raise ValueError("can't have both id and be noise")
        elif caller_id and not origin:
            raise ValueError("id only exists at origin")

        # if a packet is created for dummy/statistical noise ops
        self.noise = noise
        if self.noise:
            self.prep_noise()

        # exclusive to origin server: stores source ID
        self.caller_id = None

        # used by client and server to hold plain message
        self.contents = None

        # used by client and server to hold plain response collected from deaddrop
        self.collected = None


    # Client Tools

    # used by client to prep request
    def client_prep_up(self, pub_keys):
        if not self.client:
            raise ValueError("not a client")

        if not (self.contents.collect and self.contents.drop and self.contents.message):
            raise KeyError("missing key for client wrap")

        self.payload = json.dumps(self.contents._asdict()).encode() # payload to json str to bytes
        self.contents = None # clear

        self._onion_encrypt_pub(pub_keys)

    def _onion_encrypt_pub(self, pub_keys):
        """
        Constructs layered encryption of payload symm_keys using passed pub_keys; operates front to back.
        Stores results in payload.
        """
        if not (self.client):
            raise ValueError("only origin can use onion encryption")
        if not (self.payload):
            raise ValueError("payload missing")

        # generate and store symm_key vector
        self.symm_keys = [ec.generate_aes() for _ in pub_keys]

        onion = self._onion_encrypt_pub_helper(pub_keys, self.symm_keys, self.payload)
        self.data = onion
        self.payload = None

    @staticmethod
    def _onion_encrypt_pub_helper(pub_keys, symm_keys, payload):
        """
        Encrypts payload in an onion scheme using public key.
        Returns final result as bytes.
        Format: ENC(public key, (symm_key, nested_payload))
        """
        # recursively work from last to first (right to left)

        # base: 1 key pair; use straight up
        # recursive: more; generate and use nested payload
        payload_val = payload if len(pub_keys) == 1 else Packet._onion_encrypt_pub_helper(pub_keys[1:], symm_keys[1:], payload)

        prepped = b"".join((symm_keys[0], payload_val))

        encrypted = ec.encrypt_rsa(prepped, pub_keys[0])

        return encrypted

    def onion_decrypt_symm(self):
        """
        Strips layered encryption from data using symm_keys member; operates front to back.
        Stores results in payload; clears data.
        """
        if not self.client:
            raise ValueError("not a client")
        elif not self.data:
            raise KeyError("missing data for decrypt wrap")
        elif not (self.symm_keys and isinstance(self.symm_keys, list)):
            raise KeyError("invalid symm_keys vector")

        for k in self.symm_keys:
            self.data = ec.decrypt_aes(self.data, k)
        self.payload = self.data
        self.data = None


    # Server Tools

    # given a private key decrypts data and breaks into symm key and nested payload
    def onion_peel_layer(self, private_key):
        if self.client:
            raise ValueError("client should not use peel; only server")
        elif not isinstance(private_key, bytes):
            raise ValueError("data is missing or invalid type")
        elif not (self.data and isinstance(self.data, bytes)):
            raise ValueError("data is missing or invalid type")
        elif self.symm_keys or self.payload:
            raise ValueError("symm_key and/or payload filled; already peeled")

        unpeeled = ec.decrypt_rsa(self.data, private_key)
        self.data = None

        string_in = io.BytesIO(unpeeled) # process data string as file
        self.symm_keys, self.payload = [ string_in.read(x) for x in (ec.AES_SIZE, -1) ]


    def onion_add_layer(self):
        if self.client:
            raise ValueError("not a server")
        if not self.payload:
            raise KeyError("missing payload for decrypt")
        elif not (self.symm_keys and isinstance(self.symm_keys, bytes)):
            raise KeyError("invalid symm_keys byte string")

        self.data = ec.encrypt_aes(self.payload, self.symm_keys)
        self.payload = None

    def prep_noise(self):
        raise NotImplementedError("haven't done noise")
