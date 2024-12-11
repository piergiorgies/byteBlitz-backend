import os
from hashlib import sha256

def _hash_password(password: str, salt: str = None):
    if not salt:
        salt = os.urandom(32)
    key = sha256(salt + password.encode()).hexdigest()
    return key, salt.hex()