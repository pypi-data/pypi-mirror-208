import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from gameauth.password import encrypt as encrypt_password

ENCODING = "UTF-8"


class NoSuchUserError(Exception):
    pass


class DuplicateUserIdError(Exception):
    pass


class User:

    def __init__(self, uid: str, password: str, is_encrypted: bool = False,
                 full_name: str = None, nickname: str = None, custom: Any = None,
                 creation_date: datetime = None):
        if uid is None or password is None:
            raise ValueError("uid and password are required")
        self.uid = uid
        self.password = password if is_encrypted else encrypt_password(password)
        self.full_name = full_name
        self.nickname = nickname
        self.custom = custom
        self.creation_date = creation_date if creation_date else datetime.now().astimezone()

    def tag(self):
        md5 = hashlib.md5()
        md5.update(self.uid.encode(ENCODING))
        if self.full_name:
            md5.update(self.full_name.encode(ENCODING))
        if self.nickname:
            md5.update(self.nickname.encode(ENCODING))
        if self.custom:
            md5.update(json.dumps(self.custom).encode(ENCODING))
        return md5.hexdigest()

    def change_password(self, password: str):
        self.password = encrypt_password(password)


class UserRepository(ABC):

    @abstractmethod
    def create_user(self, uid: str, password: str, nickname: str, full_name: str,
                    custom: Any = None):
        pass

    @abstractmethod
    def delete_user(self, uid: str):
        pass

    @abstractmethod
    def find_user(self, uid: str) -> User:
        pass

    @abstractmethod
    def change_password(self, uid: str, password: str) -> None:
        pass

    @abstractmethod
    def replace_user(self, user: User) -> User:
        pass
