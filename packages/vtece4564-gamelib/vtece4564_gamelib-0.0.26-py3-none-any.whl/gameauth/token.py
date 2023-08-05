#
# Constants used in JSON Web Tokens by the token_generator.py and token_validator.py modules
#

ALGORITHM = "RS256"
ID_LENGTH = 64
LIFETIME_SECONDS = 60
LEEWAY_SECONDS = 30

JTI = "jti"
SUB = "sub"
ISS = "iss"
AUD = "aud"
IAT = "iat"
EXP = "exp"
PLY = "ply"
