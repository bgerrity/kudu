# packet.py

# wrapper and validator of 
class Packet:
    size = None # standardized size for packets

    def __init__(self, packet, terminal=False):
        self.validate()

        self.packet = packet
        self.encrypted = None
        self.decrypted = None
        
        self.terminal = terminal            
        self.collect = None
        self.drop = None
        self.message = None

    # takes decrypted value as inclear json and fill instance with its values
    # discards any extraneous values
    def unwrap(self):
        if not self.terminal:
            raise ValueError("terminal flag not up")
        if not self.decrypted:
            raise ValueError("no decrypted value")

        self.collect = self.packet.get("collect")
        self.drop = self.packet.get("drop")
        self.message = self.packet.get("message")

    # use key to store a decrypted version
    def decrypt(self, key):
        pass
        # TODO: use key to decrypt packet
        self.decrypted = self.packet
        raise NotImplementedError()

    # use key to store an encrypted version
    def encrypt(self, key):
        pass
        # TODO: use key to encrypt packet
        self.encrypted = self.packet
        raise NotImplementedError()

    def validate(self):
        self.validate_size()
        raise NotImplementedError()

    def validate_size(self):
        if len(self.packet) != self.size:
            raise ValueError("size of packet is incorrect")

        raise NotImplementedError()
