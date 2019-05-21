# packet.py

from collections import namedtuple

Contents = namedtuple("contents", ["collect", "drop", "message"])

# wrapper and validator of 
class Packet:
    size = None # standardized size for packets

    def __init__(self, packet, terminal=False):
        self.packet = packet
        Packet.validate_size(self.packet)
        
        self.contents = None

        self.symm_key = None
        self.terminal = terminal

    def decrypt_and_process(self, key):
        self.decrypt(key)
        self.unwrap()
        
    # use key to store a decrypted version
    def decrypt(self, key):
        pass
        # TODO: use key to decrypt packet
        self.packet = self.packet

        # TODO: enable with crypto
        self.validate_size()
        # raise NotImplementedError()

    # takes decrypted value as en clair json and fill instance with its values
    # discards any extraneous values
    # throws error if any not found (invalid)
    def unwrap(self):
        if self.terminal:
            self.contents = Contents(self.packet.get("collect"), self.packet.get("drop"), self.packet.get("message"))
            
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