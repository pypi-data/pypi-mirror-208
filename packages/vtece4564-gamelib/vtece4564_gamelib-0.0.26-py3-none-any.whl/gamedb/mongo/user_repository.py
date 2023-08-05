import logging

from typing import Any, Dict

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from ..user_repository import User, UserRepository, DuplicateUserIdError, NoSuchUserError


_USERS_COLLECTION_NAME = "users"
_ID_KEY = "_id"
_UID_KEY = "uid"
_CREATION_DATE_KEY = "creation_date"
_CUSTOM_KEY = "custom"
_FULL_NAME_KEY = "full_name"
_NICKNAME_KEY = "nickname"
_PASSWORD_KEY = "password"

logger = logging.getLogger(__name__)


class MongoUser(User):

    @classmethod
    def from_dict(cls, rec: dict) -> "MongoUser":
        record = MongoUser(rec.get(_UID_KEY), rec.get(_PASSWORD_KEY), is_encrypted=True, custom=rec.get(_CUSTOM_KEY),
                           creation_date=rec.get(_CREATION_DATE_KEY))
        record.nickname = rec.get(_NICKNAME_KEY)
        record.full_name = rec.get(_FULL_NAME_KEY)
        record.custom = rec.get(_CUSTOM_KEY)
        return record

    def to_dict(self) -> Dict:
        record = {
            _UID_KEY: self.uid,
            _PASSWORD_KEY: self.password,
            _CREATION_DATE_KEY: self.creation_date,
        }
        if self.full_name:
            record.update({_FULL_NAME_KEY: self.full_name})
        if self.nickname:
            record.update({_NICKNAME_KEY: self.nickname})
        if self.custom:
            record.update({_CUSTOM_KEY: self.custom})
        return record


class MongoUserRepository(UserRepository):

    def __init__(self, mongo: MongoClient):
        self.users: Collection = mongo.get_default_database().get_collection(_USERS_COLLECTION_NAME)
        self.users.create_index(_UID_KEY, unique=True)

    def create_user(self, uid: str, password: str, nickname: str = None, full_name: str = None, custom: Any = None):
        user = MongoUser(uid, password, is_encrypted=False, nickname=nickname, full_name=full_name, custom=custom)
        user_doc = user.to_dict()
        try:
            logger.debug(f"inserting user: {user_doc}")
            doc_id = self.users.insert_one(user_doc).inserted_id
            user_doc = self.users.find_one({_ID_KEY: doc_id})
            return MongoUser.from_dict(user_doc)
        except DuplicateKeyError:
            raise DuplicateUserIdError(f"user with ID {user.uid} already exists")

    def delete_user(self, uid: str):
        self.users.delete_one({_UID_KEY: uid})

    def find_user(self, uid: str) -> User:
        user_doc = self.users.find_one({_UID_KEY: uid})
        if user_doc is None:
            raise NoSuchUserError(f"user ID {uid} not found")
        return MongoUser.from_dict(user_doc)

    def change_password(self, uid: str, password: str) -> None:
        user_doc = self.users.find({_UID_KEY: uid})
        if user_doc is None:
            raise NoSuchUserError(f"user ID {uid} not found")

        user = MongoUser.from_dict(user_doc)
        user.change_password(password)
        user_doc = user.to_dict()
        self.users.update_one({_UID_KEY: uid}, user_doc)

    def replace_user(self, user: User) -> User:
        user_doc = self.users.find({_UID_KEY: user.uid})
        if user_doc is None:
            raise NoSuchUserError(f"user ID {user.uid} not found")

        db_user = MongoUser.from_dict(user_doc)
        db_user.nickname = user.nickname
        db_user.full_name = user.full_name
        db_user.custom = user.custom
        user_doc = db_user.to_dict()
        self.users.update_one({_UID_KEY: user.uid}, user_doc)
        return db_user