# packet.py

import random

# A representation of inter-server communication: Namely, the list of operable
# requests to be fulfilled for a client (a bundle of packets).
# Includes facilites for core Vuvuzela operations:
# Encryption, decryption, shuffle, and unshuffle.
class Bundle:
    def __init__(self, packets=[]):
        self.packets = packets
        self._shuffle_key = None

    def add_packet(self, packet):
        self.packets.append(packet)

    def prep_forward(self, key):
        self.decrypt_packets(key)
        self.forward_shuffle_packets()

    def prep_reverse(self, key):
        self.decrypt_packets(key)
        self.reverse_shuffle_packets()

    def encrypt_packets(self, key):
        for p in self.packets:
            p.encrypt(key)
        raise NotImplementedError("Bundle.encrypt_packets")

    def decrypt_packets(self, key):
        for p in self.packets:
            p.decrypt(key)
        raise NotImplementedError("Bundle.decrypt_packets")

    # shuffles the bundled packets using an optionally provided key
    # returns shuffle map (list of original indices)
    def forward_shuffle_packets(self):
        if self._shuffle_key:
            raise ValueError("already shuffled")

        indexed = list(enumerate(self.packets))
        random.shuffle(indexed)

        self.packets = [packet for _, packet in indexed]
        self._shuffle_key = [i for i, _ in indexed]

    # given the key, performs the unshuffle
    def reverse_shuffle_packets(self):
        if not self._shuffle_key:
            raise ValueError("not shuffled")

        self.packets = [packet for _, packet in \
            sorted(zip(self._shuffle_key, self.packets), key=lambda x: x[0])]
        self._shuffle_key = None
