# server/server.py

import os, sys
from enum import Enum
from collections import OrderedDict

sys.path.append(os.path.abspath('../Kudu'))

import lib.easy_crypto as ec
import lib.payload as pl

from packet import Packet
from bundle import Bundle

class Server:
    """
    Server state and processing: Hosts the server's business logic;
    could be attached to database and converted to interface for RESTful api.
    """
    class Modes(Enum):
        RECEIVING = 1
        PROCESSING = 2
        DISTRIBUTING = 3

    def __init__(self, client_count=2, server_count=5):
        self.CLIENT_COUNT = client_count
        self.SERVER_COUNT = server_count

        # vector of server keys
        self._keys = [ec.generate_rsa() for _ in range(self.SERVER_COUNT)]

        self.current_round = 0
        self.mode = Server.Modes.RECEIVING

        self._id_map = OrderedDict() # {id: data}
        self._responses = None # {id: deaddrop_result}

        # TODO: refactor out
        self._bundles = None # representation of each servers internal state

    def get_public_keys(self):
        return [ec.export_rsa_public(k).decode() for k in self._keys]

    def reset(self):
        if self.mode != Server.Modes.DISTRIBUTING:
            raise ValueError("not ready to reset")

        self.current_round += 1
        self.mode = Server.Modes.RECEIVING

        self._id_map = OrderedDict()
        self._responses = None

        self._bundles = None # regenerate each round

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
