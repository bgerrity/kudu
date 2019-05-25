# client/packet.py

import json, io
from collections import namedtuple

import lib.easy_crypto as ec


# wrapper and validator
class Packet:
    size = None # standardized size for packets

    def __init__(self):
        # raw data recieved for processing; initial
        self._inbox = None
        # processed data to be sent onward
        self._outbox = None

        # the key to be collected on pass-up and used on the pass-down
        self._symm_keys = None

        # if a packet is created for dummy/statistical noise ops
        self.noise = False

        self.payload = None

        self.caller_id = None

    def client_prep_up(self, pub_keys):
        """
        Onion-encrypts the payload using param pub_keys (first_key -> outermost_enc).
        Generates a symm_keys vector for the field and nests.
        Stores results in data field; clears payload and contents fields. 
        """
        if not self.payload:
            raise ValueError("payload not filled")

        # generate symm_keys
        self._symm_keys = [ec.generate_aes() for _ in pub_keys]
        # use keys to make an onion
        onion = Packet._onion_encrypt_pub(pub_keys, self._symm_keys, self.payload)
        self._outbox = onion

    def send_out(self):
        outbound =  self._outbox
        self._outbox = None
        return outbound

    @staticmethod
    def _onion_encrypt_pub(pub_keys, symm_keys, payload):
        """
        Encrypts payload in an onion scheme using public key (nests one symm_key in each layer)
        Returns final result as bytes.
        Format: ENC(public key, (symm_key, nested_payload))
        """

        # recursively work from last to first (right to left)

        # base: 1 key pair; use straight up
        # recursive: more; generate and use nested payload
        payload_val = payload if len(pub_keys) == 1 else Packet._onion_encrypt_pub(pub_keys[1:], symm_keys[1:], payload)

        prepped = b"".join((symm_keys[0], payload_val))

        encrypted = ec.encrypt_rsa(prepped, pub_keys[0])

        return encrypted

    def onion_decrypt_symm(self):
        """
        Strips layered encryption from data using symm_keys member; operates front to back.
        Stores results in payload; clears inbox and symm_keys.
        """

        if self._outbox:
            raise ValueError("outbox already filled")
        elif not self._inbox:
            raise ValueError("missing data for decrypt unwrap")
        elif not (self._symm_keys and isinstance(self._symm_keys, list)):
            raise ValueError("invalid symm_keys vector")

        work = self._inbox
        for k in self._symm_keys:
            work = ec.decrypt_aes(work, k)
        self._outbox = work
        self._inbox = None
        self._symm_keys = None
