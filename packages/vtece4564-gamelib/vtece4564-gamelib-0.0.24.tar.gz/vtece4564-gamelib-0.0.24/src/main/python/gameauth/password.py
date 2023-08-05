from purecrypt import Crypt, Method

_CRYPT_METHOD = Method.SHA512
_CRYPT_ROUNDS = 10000


def encrypt(plaintext_password: str, salt: str = None):
    """
    Encrypts a password for storage or comparison.
    :param plaintext_password: plaintext password
    :param salt: salt to use in the encryption; specify None to generate a new salt, or specify the salt of the
        password to be compared (only that substring that represents a salt will be used)
    :return: the encyrpted password
    """
    # Generate a temporary salt so that we know the length of the salt
    temp_salt = Crypt.generate_salt(_CRYPT_METHOD, rounds=_CRYPT_ROUNDS)
    if salt is not None:
        # Extract the salt from whatever else is in the string
        salt = salt[:len(temp_salt)]
    else:
        # Use the generated salt
        salt = temp_salt

    ciphertext_password = Crypt.encrypt(plaintext_password, salt)
    return ciphertext_password


def is_valid(plaintext_password: str, encrypted_password: str):
    """
    Tests whether a plaintext password matches an encrypted password.
    :param plaintext_password: the password to be test
    :param encrypted_password: the basis for the comparison
    :return: s
    """
    return Crypt.is_valid(plaintext_password, encrypted_password)
