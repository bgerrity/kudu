import io
from collections import namedtuple

Payload = namedtuple("payload", ["collect", "drop", "message"])

ADDRESS_SIZE = 256 # size of shared secret used by
MESSAGE_SIZE = 512 # arbitrary size

def export_payload(payload):
    """
    Given a payload object, generates a binary instances
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
    string_in = io.BytesIO(data) # process data string as file

    collect, drop, message = \
        [ string_in.read(x) for x in (ADDRESS_SIZE, ADDRESS_SIZE, MESSAGE_SIZE) ]

    return Payload(collect, drop, message)
