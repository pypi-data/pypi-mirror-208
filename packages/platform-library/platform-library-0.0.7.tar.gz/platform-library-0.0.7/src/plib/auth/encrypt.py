import hashlib
from typing import Optional
from uuid import uuid4


class Encryptor:
    def __init__(self, salt: str, signature: Optional[str] = None):
        self.__salt = salt
        self.__signature = signature if signature else str(uuid4())

    @property
    def signature(self) -> str:
        return self.__signature

    def validate(self, enrypted_signature: str) -> bool:
        return enrypted_signature == self.encrypt()

    def encrypt(self) -> str:
        return hashlib.sha256((self.__signature + self.__salt).encode('utf8')).hexdigest()
