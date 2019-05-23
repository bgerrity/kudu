#! /usr/bin/env python3
# easy_crypto.py

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import io

# shamelessly stolen from https://pycryptodome.readthedocs.io/en/latest/src/examples.html

# generate a standard RsaKey instance
def generate_rsa():
    """Generate a standard RsaKey instance."""
    return RSA.generate(2048)

# given an rsa key, returns an export format public key
def export_rsa_public(key):
    """Returns an export format public key given an rsa key."""
    if not isinstance(key, RSA.RsaKey):
        raise ValueError("param @key must be type RsaKey")

    return key.publickey().export_key()

# given an rsa key, returns an export format private key
def export_rsa_private(key):
    """Returns an export format private key given an rsa key."""
    if not isinstance(key, RSA.RsaKey):
        raise ValueError("param @key must be type RsaKey")

    return key.export_key()

# given bytes data and exported public_key
# returns encrypted bytes
def encrypt_rsa(data, public_key):
    """Encrypts data given a key."""
    if not isinstance(data, bytes):
        raise ValueError("param @data must be type bytes")
    if not isinstance(public_key, bytes):
        raise ValueError("param @public_key must be type bytes")


    recipient_key = RSA.import_key(public_key)
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)
    return b"".join((enc_session_key, cipher_aes.nonce, tag, ciphertext))

# given bytes data and exported private_key
# returns decrypted bytes
def decrypt_rsa(data, private_key):
    """Decrypts data given a key."""
    if not isinstance(data, bytes):
        raise ValueError("param @data must be type bytes")
    if not isinstance(private_key, bytes):
        raise ValueError("param @private_key must be type bytes")


    string_in = io.BytesIO(data) # process data string as file

    private_key = RSA.import_key(private_key)

    enc_session_key, nonce, tag, ciphertext = \
    [ string_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    plaintext = cipher_aes.decrypt_and_verify(ciphertext, tag)

    return plaintext

# returns aes key as bytes
def generate_aes():
    """Generate an AES key."""
    key = get_random_bytes(16)
    return key

# given bytes data and AES key
# returns encrypted bytes
def encrypt_aes(data, key):
    """Encrypts data given a key."""
    if not isinstance(data, bytes):
        raise ValueError("param @data must be type bytes")
    if not isinstance(key, bytes):
        raise ValueError("param @key must be type bytes")


    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    return b"".join((cipher.nonce, tag, ciphertext))

# given bytes data and AES key
# returns decrypted bytes
def decrypt_aes(data, key):
    """Decrypts data given a key."""
    if not isinstance(data, bytes):
        raise ValueError("param @data must be type bytes")
    if not isinstance(key, bytes):
        raise ValueError("param @key must be type bytes")


    string_in = io.BytesIO(data) # process data string as file

    nonce, tag, ciphertext = [ string_in.read(x) for x in (16, 16, -1) ]

    # let's assume that the key is somehow available again
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

    return plaintext

# TESTING SCRIPT
if __name__ == '__main__':
    rsa_plain = "life is like a box of chocolates".encode("utf-8")

    rsa_key = generate_rsa()

    p_export = export_rsa_public(rsa_key)
    s_export = export_rsa_private(rsa_key)

    rsa_encrypted = encrypt_rsa(rsa_plain, p_export)
    rsa_decrypted = decrypt_rsa(rsa_encrypted, s_export)

    print(rsa_decrypted.decode("utf-8"))


    aes_plain = "full of surprises".encode("utf-8")

    aes_key = generate_aes()

    aes_encrypted = encrypt_aes(aes_plain, aes_key)
    aes_decrypted = decrypt_aes(aes_encrypted, aes_key)


    print(aes_decrypted.decode("utf-8"))