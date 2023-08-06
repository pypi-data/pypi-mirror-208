import jwt
from typing import List


def decode_payload(encoded_payload: str, secret: str, algorithms: List[str]):
    return jwt.decode(encoded_payload, secret, algorithms=algorithms)


def encode_payload(payload: dict, key: str, algorithm: str):
    return jwt.encode(payload, key=key, algorithm=algorithm)
