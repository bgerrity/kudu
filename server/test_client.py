import requests

import json

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

with open("server/fixed-key.pem", "rb") as f:
    s_key = RSA.import_key(f.read())


data54 = {
        "symm_key": "foo",
        "payload" : {
            "collect": "12",
            "drop": "13",
            "message": "my mother told me -- from 54"
        }
    }

data55 = {
    "symm_key": "bar",
    "payload" : {
        "collect": "13",
        "drop": "12",
        "message": "life is like a box of chocolates -- from 55"
    }
}



obj54 = json.dumps(data54)
obj55 = json.dumps(data55)

cipher_rsa = PKCS1_OAEP.new(s_key)

ciphertext54 = cipher_rsa.encrypt(obj54.encode())
ciphertext55 = cipher_rsa.encrypt(obj55.encode())


response = requests.post(
    'http://127.0.0.1:5001/submission/54',
    data=ciphertext54
)

response = requests.post(
    'http://127.0.0.1:5001/submission/55',
    data=ciphertext55
)


# decipher_rsa = PKCS1_OAEP.new(s_key)
# dec = decipher_rsa.decrypt(ciphertext)

# print(dec)