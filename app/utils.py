import hashlib
import secrets

def generate_salt():
    return secrets.token_hex(8)

def hash_password(password: str, salt: str):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def calculate_new_marks(existing: int, new: int) -> int:
    return existing + new
