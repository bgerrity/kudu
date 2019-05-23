#! /usr/bin/env python3

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
import requests
import sys
import time

class Client:
    def __init__(self): # TODO: args
        self.id = sys.argv[1]
        self.keys = self.generate_key(1) # [ ( public, secret ) ]
        self.partner = sys.argv[2]
        self.partner_key = None

    # listen-print-eval-loop
    def listen(self):
        raise NotImplementedError


    # generate pair of keys for this client
    def generate_key(self, count):
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return [private_key, public_key]

    # query dispatch for its partner (may be none)
    def get_partner(self):
        return 0 # TODO this might change

    # query user for message to send
    def collect_message(self):
        raise NotImplementedError

    # instantiate round struct
    def create_round(self):
        raise NotImplementedError

    # instantiate noise message
    def create_round_noise(self):
        raise NotImplementedError

    # send up to server
    def send_round(self):
        raise NotImplementedError

    # collect server
    def collect_round(self):
        raise NotImplementedError

    # wrappers for openssl
    def encrypt(self):
        raise NotImplementedError

    def decrypt(self):
        raise NotImplementedError

def exchangeKeys():
    response = requests.post('http://127.0.0.1:5000/publish_key/'+ client.id, data = client.keys[1])
    print("Public Key posted")
    time.sleep(2)
    response2 = requests.get('http://127.0.0.1:5000/get_key/' + client.partner)

    print(response2.content)

message = ""
client = Client()
print("Client ", client.id, "partner ", client.partner)
exchangeKeys()

while message != "Quit":
    message = input("Enter message: ")
