import sys, os
sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec

k = (ec.generate_aes(), ec.generate_aes(), ec.generate_aes())

plain = "fe fi fo fum".encode()

enc0 = ec.encrypt_aes(plain, k[0])

enc1 = ec.encrypt_aes(enc0, k[1])

enc2 = ec.encrypt_aes(enc1, k[2])

dec2 = ec.decrypt_aes(enc2, k[2])

dec1 = ec.decrypt_aes(dec2, k[1])

dec0 = ec.decrypt_aes(dec1, k[0])


print(dec0)