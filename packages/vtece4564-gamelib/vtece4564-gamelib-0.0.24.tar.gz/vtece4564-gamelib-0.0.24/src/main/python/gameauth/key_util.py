import getpass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

PASSPHRASE_ENCODING = "UTF-8"
PUBLIC_EXPONENT = 65537
KEY_SIZE_BITS = 2048


def generate_key_pair():
    private_key = rsa.generate_private_key(PUBLIC_EXPONENT, KEY_SIZE_BITS)
    public_key = private_key.public_key()
    return private_key, public_key


def load_private_key(filename: str, passphrase: str):
    passphrase = passphrase.encode(PASSPHRASE_ENCODING)
    with open(filename, "rb") as input_file:
        key_bytes = input_file.read()
        return serialization.load_pem_private_key(key_bytes, passphrase)


def store_private_key(private_key, filename: str, passphrase: str):
    passphrase = passphrase.encode(PASSPHRASE_ENCODING)
    with open(filename, "w+b") as output_file:
        output_file.write(private_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                                    serialization.BestAvailableEncryption(password=passphrase)))


def load_public_key(filename: str):
    with open(filename, "rb") as input_file:
        key_bytes = input_file.read()
        return serialization.load_pem_public_key(key_bytes)


def store_public_key(public_key, filename: str):
    with open(filename, "w+b") as output_file:
        output_file.write(public_key.public_bytes(serialization.Encoding.PEM,
                                                  serialization.PublicFormat.SubjectPublicKeyInfo))



