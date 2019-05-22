# packet.py

import json
from collections import namedtuple

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

Contents = namedtuple("contents", ["collect", "drop", "message"])

# wrapper and validator of
class Packet:
    size = None # standardized size for packets

    def __init__(self, data, terminal=False):
        self.packet = data
        Packet.validate_size(self.packet)

        self.symm_key = None # the key used for encrypting back down the chain
        self.payload = None # the binary string to pass up the chain

        self.contents = None # stores parameters for deaddrop ops

        self.symm_key = None
        self.terminal = terminal

    def decrypt_and_process(self, key):
        self.decrypt(key)
        self.unwrap()

    # use key to store a decrypted version
    def decrypt(self, key_string):
        key = RSA.import_key(key_string)
        decipher_rsa = PKCS1_OAEP.new(key)
        self.packet = decipher_rsa.decrypt(self.packet).decode()

    # takes decrypted value as en clair json and fill instance with its values
    # discards any extraneous values
    # throws error if any not found (invalid)
    def unwrap(self):
        unwrapped = json.loads(self.packet)
        self.symm_key = unwrapped.get("symm_key")
        self.payload = unwrapped["payload"]

        # if terminal, then symmetric key is done: can directly access payload
        if self.terminal:
            self.contents = Contents(
                self.payload.get("collect"),
                self.payload.get("drop"),
                self.payload.get("message")
            )

            if not (self.contents.collect and self.contents.drop and self.contents.message):
                raise ValueError("missing key for unwrap")
        else:
            raise NotImplementedError("intermediate chained server")


    # use key to store an encrypted version
    def encrypt(self, key):
        pass
        # TODO: use key to encrypt packet
        self.packet = self.packet

        # TODO: enable with crypto
        self.validate_size()
        # raise NotImplementedError()

    def validate(self):
        self.validate_size()
    #     raise NotImplementedError()

    # checks passed object against size constraint
    def validate_size(self):
        pass
        # if len(packet) != Packet.size: # TODO: enable
        #     raise ValueError("size of packet is incorrect")
        #
        # raise NotImplementedError()