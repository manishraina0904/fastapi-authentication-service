import hashlib
import uuid


def hash_password(password: str):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def verify_password(password: str, hashed: str):

    return hashlib.sha256(
        password.encode()
    ).hexdigest() == hashed


def create_refresh_token():
    return str(uuid.uuid4())