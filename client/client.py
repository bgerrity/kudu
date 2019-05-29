#! /usr/bin/env python3

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from http import HTTPStatus
import requests, os, sys, time

sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec


class Client:
    def __init__(self): # TODO: args
        self.id = sys.argv[1]
        self.keys = self.generate_key(1) # [ ( private, public ) ]
        self.partner = sys.argv[2]
        self.DH_key = self.generate_DH()
        self.partner_key = None
        self.shared_secret = None

    # listen-print-eval-loop
    def listen(self):
        raise NotImplementedError


    def generate_DH(self):
        private_key = ec.generate_dh()
        return private_key

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

'''def exchangeKeys():
    response = requests.post('http://127.0.0.1:5000/publish_key/'+ client.id, data = client.keys[1])
    print(response.status_code)

    if response.status_code == HTTPStatus.ACCEPTED:
        print("Public Key posted")

    response2 = requests.get('http://127.0.0.1:5000/get_key/' + client.partner)
    while(response2.status_code != HTTPStatus.ACCEPTED):
        time.sleep(1)
        response2 = requests.get('http://127.0.0.1:5000/get_key/' + client.partner)'''

def postKeys():
    # posts the public RSA key to the server
    response = requests.post('http://127.0.0.1:5000/publish_key/'+ client.id, data = client.keys[1])
    if response.status_code == HTTPStatus.ACCEPTED:
        print("Public Key posted")

    # posts the diffie hellman public key to the server
    # TODO change DH_public according to the new return value in easy_crypto
    DH_public = str(ec.DH_get_public_key(client.DH_key)).encode()
    print(ec.DH_get_public_key(client.DH_key))
    response2 = requests.post('http://127.0.0.1:5000/publish_DH_key/'+ client.id, data = DH_public)
    if response2.status_code == HTTPStatus.ACCEPTED:
        print("Public DH Key posted")

    # when done with posting keys increments the number of users
    response3 = requests.post('http://127.0.0.1:5000/increment_users')
    if response3.status_code == HTTPStatus.ACCEPTED:
        print("Client finished posting")

def getKeys():
    response = requests.get('http://127.0.0.1:5000/get_key/' + client.partner)
    while(response.status_code != HTTPStatus.ACCEPTED):
        time.sleep(1)
        response = requests.get('http://127.0.0.1:5000/get_key/' + client.partner)
    client.partner_key = response.content

    response2 = requests.get('http://127.0.0.1:5000/get_DH_key/' + client.partner)
    while(response2.status_code != HTTPStatus.ACCEPTED):
        time.sleep(1)
        response2 = requests.get('http://127.0.0.1:5000/get_DH_key/' + client.partner)

    #TODO: figure out how to get the key in response2 to the client
    '''peer_public_key = str(response2.content.decode())
    print(type(peer_public_key))
    print(type(response2.content))
    print(response2.content)'''

message = ""
client = Client()
print("Client ", client.id, "partner ", client.partner)
#postKeys()
#getKeys()


while message != "Quit":
    message = input("Enter message: ")
