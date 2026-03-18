import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return hashlib.sha256(password) == hashed_password

