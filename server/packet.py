# packet.py

# wrapper and validator of 
class Packet:
    size = None # standardized size for packets

    def __init__(self, packet):
        self.packet = packet
        Packet.validate_size(self.packet)
        
        self.collect = None
        self.drop = None
        self.message = None

    # takes decrypted value as en clair json and fill instance with its values
    # discards any extraneous values
    # throws error if any not found (invalid)
    def unwrap(self):
        if not self.decrypted:
            raise ValueError("no decrypted value")

        self.collect = self.packet.get("collect")
        self.drop = self.packet.get("drop")
        self.message = self.packet.get("message")

        if not (self.collect and self.drop and self.message):
            raise ValueError("missing key for unwrap")

    # use key to store a decrypted version
    def decrypt(self, key):
        pass
        # TODO: use key to decrypt packet
        self.packet = self.packet

        # TODO: enable with crypto
        self.validate_size()
        # raise NotImplementedError()

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