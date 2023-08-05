from typing import Dict

import jwt
from .token import *
from .key_util import load_public_key


class InvalidTokenError(Exception):
    pass


class TokenValidator:
    """ A validation service for JWT-based authentication tokens """

    def __init__(self, issuer_uri: str, public_key_filename: str, token_leeway_seconds: int = LEEWAY_SECONDS):
        """
        Creates a new token validator.
        :param issuer_uri: the identifier to expect in the issuer claim (`iss`) of each token
        :param public_key_filename: file/path name for the public key to use in validating token signatures
        :param token_leeway_seconds: number of seconds of leeway to allow for token expiration
        """
        self.issuer_uri = issuer_uri
        self.token_leeway_seconds = token_leeway_seconds
        self.public_key = load_public_key(public_key_filename)

    def validate(self, gid: str, token: str) -> Dict:
        """
        Validates a token and returns the claims from the token.
        In order to be considered valid, the token must satisfy all of the following requirements:
        1. The token must have been signed using the RSA256 algorithm with the private key counterpart
           to the public key configured for this validator.
        2. The token must have an expiration claim (`exp`) within the leeway configured for this validator.
        3. The token must have an issuer claim (`iss`) that matches the issuer URI configured for this validator.
        4. The token must have an audience claim (`aud`) that contains the given game ID.
        5. The token must have the following additional claims: `jti`, `sub`, `iat`, `ply`.
        :returns: dictionary of token claims
        :raises InvalidTokenError: if the token is deemed invalid
        """
        try:
            return jwt.decode(token, self.public_key, algorithms=[ALGORITHM], verify=True,
                              issuer=self.issuer_uri, audience=gid, leeway=self.token_leeway_seconds,
                              required=[JTI, ISS, SUB, IAT, EXP, AUD, PLY])
        except Exception as err:
            raise InvalidTokenError(str(err)) from err
