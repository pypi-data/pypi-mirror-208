import random
from datetime import datetime, timedelta
from typing import Iterable

import jwt

from .token import *
from .key_util import load_private_key


class TokenGenerator:
    """ A generator service for JWT authentication tokens """

    def __init__(self, issuer_uri: str, private_key_filename: str, private_key_passphrase: str,
                 token_lifetime_seconds: int = LIFETIME_SECONDS):
        """
        Creates a new token validator.
        :param issuer_uri: the identifier to include as the issuer claim (`iss`) in each token
        :param private_key_filename: file/path name for the private key to use to sign tokens
        :param private_key_passphrase: passphrase that will be used to decrypt the private key
        :param token_lifetime_seconds: number of seconds of lifetime for each token
        """
        self.issuer_uri = issuer_uri
        self.token_lifetime_seconds = token_lifetime_seconds
        self.private_key = load_private_key(private_key_filename, private_key_passphrase)

    def generate(self, uid, gid: str, players: Iterable[str]) -> str:
        """
        Generates an authentication for the given user and collection of authorized game IDs
        :param uid: unique ID for the user
        :param gid: unique ID for the games to authorize
        :param players: iterable collection of player user IDs
        :return: return the signed authentication token
        """
        jti = random.randbytes(ID_LENGTH // 8).hex()
        iat = datetime.utcnow()
        exp = iat + timedelta(seconds=self.token_lifetime_seconds)
        claims = {
            JTI: jti,
            SUB: uid,
            AUD: gid,
            ISS: self.issuer_uri,
            IAT: iat,
            EXP: exp,
            PLY: tuple(players)
        }
        return jwt.encode(claims, self.private_key, algorithm=ALGORITHM)
