# server/bundle.py

import os, sys, random

sys.path.append(os.path.abspath('../Kudu'))

from packet import Packet

class Bundle:
    """
    A representation of inter-server communication: Namely, the list of operable
    requests to be fulfilled for a client (a bundle of packets).
    Includes facilites for core Vuvuzela operations: Encryption, decryption,
    shuffle, and unshuffle.
    TODO: inter-server noise generation and filtering.
    """
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
