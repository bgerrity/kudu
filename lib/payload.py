#! /usr/bin/env python3
# lib/payload.py

import io
from collections import namedtuple

# a standardized format for the 3-tuple used to interact with Vuvuzela servers and clients
Payload = namedtuple("payload", ["collect", "drop", "message"])

ADDRESS_SIZE = 256 # size of shared secret used by
MESSAGE_SIZE = 512 # arbitrary size

def export_payload(payload):
    """
    Given a payload object, generates a binary instance, validating the size of each attribute.
    Note all fields in payload must be bytes.
    """

    if not isinstance(payload, Payload):
        raise ValueError("payload must be of type payload.Payload")
    elif not (isinstance(payload.collect, bytes) and len(payload.collect) == ADDRESS_SIZE):
        raise ValueError(f"collect must be bytes and length {ADDRESS_SIZE}")
    elif not (isinstance(payload.drop, bytes) and len(payload.drop) == ADDRESS_SIZE):
        raise ValueError(f"drop must be bytes and length {ADDRESS_SIZE}")
    elif not (isinstance(payload.message, bytes) and len(payload.message) == MESSAGE_SIZE):
        raise ValueError(f"drop must be bytes and length {MESSAGE_SIZE}")

    return b"".join((payload.collect, payload.drop, payload.message))


def import_payload(data):
    """
    Given bytes data, generates a Payload instance, validating the size.
    Note all fields in payload must be bytes.
    """
    if not isinstance(data, bytes):
        raise TypeError(f"data must be bytes")
    if len(data) != (ADDRESS_SIZE + ADDRESS_SIZE + MESSAGE_SIZE):
        raise ValueError(f"data is incorrect size: \
            expected sum(addr:{ADDRESS_SIZE}, addr:{ADDRESS_SIZE}, msg:{MESSAGE_SIZE}) got {len(data)}")
 
    string_in = io.BytesIO(data) # process data string as file

    collect, drop, message = \
        [ string_in.read(x) for x in (ADDRESS_SIZE, ADDRESS_SIZE, MESSAGE_SIZE) ]

    return Payload(collect, drop, message)
