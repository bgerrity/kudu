#! /usr/bin/env python3
# lib/payload.py

import io, sys, os
from collections import namedtuple

sys.path.append(os.path.abspath('../Kudu'))

import lib.easy_crypto as ec

# a standardized format for the 3-tuple used to interact with Vuvuzela servers and clients
# all fields should be bytes and message should be encrypted
Payload = namedtuple("Payload", ["collect", "drop", "message"])

ADDRESS_SIZE = 256 # size of shared secret used by
MESSAGE_SIZE = 256 # paper spec; inclusive of header

# PAYLOAD (DEADDROP EXCHANGE) HANDLING

def export_payload(payload):
    """
    Given a Payload object, generates a binary instance, validating the size of the addresses.
    Note all fields in payload must be bytes; message should be encrypted.
    """

    if not isinstance(payload, Payload):
        raise ValueError("payload must be of type payload.Payload")
    elif not (isinstance(payload.collect, bytes) and len(payload.collect) == ADDRESS_SIZE):
        raise ValueError(f"collect must be bytes and length {ADDRESS_SIZE}")
    elif not (isinstance(payload.drop, bytes) and len(payload.drop) == ADDRESS_SIZE):
        raise ValueError(f"drop must be bytes and length {ADDRESS_SIZE}")

    joined = b"".join((payload.collect, payload.drop, payload.message))

    return joined

def import_payload(data):
    """
    Given bytes data, generates a Payload instance.
    Note all fields in payload must be bytes.
    """

    if not isinstance(data, bytes):
        raise TypeError(f"data must be bytes")

    string_in = io.BytesIO(data) # process data string as file

    collect, drop, message = \
        [ string_in.read(x) for x in (ADDRESS_SIZE, ADDRESS_SIZE, -1) ]

    return Payload(collect, drop, message)

# MESSAGE HANDLING

# initial bytes in message body to store information
# [0]: message_text_length
# [1]: noise_flag: an integer
# [2-7]: unallocated
MESSAGE_HEADER_SIZE = 8
MESSAGE_BODY_SIZE = MESSAGE_SIZE - MESSAGE_HEADER_SIZE
MTL = 0 # index for message_text_length
NF = 1 # index for noise flag

SIG_INDICATOR = b"S" # byte value to indicate a message is significant (i.e. not noise)

def construct_message(plain, pub_key):
    """
    Given a plaintext string, validates as a message (length and content),
    encrypts using provided key, and returns as formatted message ready to payload.
    """
    if not isinstance(plain, str):
        raise TypeError("plain must be of type str")

    try:
        encoded = plain.encode("ascii")
    except UnicodeEncodeError:
        raise ValueError("plain must be exclusively ascii characters")

    if len(encoded) > MESSAGE_BODY_SIZE:
        raise ValueError(f"plain must be maximum {MESSAGE_BODY_SIZE} chars got {len(encoded)}")

    # encode plain's length
    msg_length = len(encoded).to_bytes(1, byteorder=sys.byteorder)

    # generate the header
    header_useful = b"".join([msg_length, SIG_INDICATOR]) # the used parts
    # append random and take the appropriate length
    header = b"".join([header_useful, os.urandom(MESSAGE_HEADER_SIZE)])[:MESSAGE_HEADER_SIZE]

    # finally the full message -- take the correct length
    result = b"".join([header, encoded, os.urandom(MESSAGE_SIZE)])[:MESSAGE_SIZE]

    return ec.encrypt_rsa(result, pub_key)

def construct_noise(pub_key):
    """
    Generates random bytes to fill message, encrypts using provided key,
    and returns as formatted message ready to payload.
    """

    # generate random
    raw = os.urandom(MESSAGE_SIZE)

    # replace until not an indicator
    while raw[NF] == SIG_INDICATOR:
        raw[NF] = os.urandom(1)

    return ec.encrypt_rsa(raw, pub_key)

Received = namedtuple("Received", ["noise", "plain"])

def deconstruct_message(encoded, priv_key):
    """
    Given encrypted bytes, decrypts, validates as a message (length and content),
    and returns as formatted message ready to payload.
    """
    if not isinstance(encoded, bytes):
        raise TypeError("encoded must be of type bytes")

    decrypted = ec.decrypt_rsa(encoded, priv_key)

    string_in = io.BytesIO(decrypted) # process data string as file

    # partition in header and dump then body
    msg_length, noise_flag, _, body = [ string_in.read(x) for x in (1, 1, 6, -1) ]

    if noise_flag != SIG_INDICATOR: # is noise
        return Received(True, None)

    # process
    msg_length = int.from_bytes(msg_length, byteorder=sys.byteorder) # header to int

    # drop padding
    encoded = body[:msg_length]

    try:
        plain = encoded.decode("ascii")
    except UnicodeDecodeError:
        raise ValueError("could not decode ascii")

    if len(encoded) > MESSAGE_BODY_SIZE:
        raise ValueError(f"plain must be maximum {MESSAGE_BODY_SIZE} chars got {len(encoded)}")

    return Received(False, plain)
