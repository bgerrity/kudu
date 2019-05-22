from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

clear = "The delivery makes the joke.".encode("utf-8")

p_key = RSA.import_key(public_key)
cipher_rsa = PKCS1_OAEP.new(p_key)
ciphertext = cipher_rsa.encrypt(clear)

print("clear:")
print(clear)
print("ciphertext:")
print(ciphertext)

s_key = RSA.import_key(private_key)
decipher_rsa = PKCS1_OAEP.new(s_key)
data = decipher_rsa.decrypt(ciphertext)

print(data)