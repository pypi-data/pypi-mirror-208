import hashlib
import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, Optional, Any

ENCODING = "UTF-8"


class NoSuchGameError(Exception):
    pass


class Game:

    def __init__(self, creator: str, players: Iterable[str], gid: str = None, custom: Any = None,
                 creation_date: datetime = None):
        self.creator = creator
        self.players = tuple(players)
        self.gid = gid if gid else str(uuid.uuid4())
        self.creation_date = creation_date if creation_date else datetime.now().astimezone()
        self.custom = custom

    def tag(self):
        md5 = hashlib.md5()
        md5.update(self.gid.encode(ENCODING))
        md5.update(self.creator.encode(ENCODING))
        if self.players:
            md5.update(json.dumps(self.players).encode(ENCODING))
        if self.custom:
            md5.update(json.dumps(self.custom).encode(ENCODING))
        return md5.hexdigest()


class GameRepository(ABC):

    @abstractmethod
    def create_game(self, creator: str, players: Iterable[str], custom: Any = None) -> Game:
        pass

    @abstractmethod
    def delete_game(self, gid: str):
        pass

    @abstractmethod
    def replace_game(self, game: Game) -> Game:
        pass

    @abstractmethod
    def find_game(self, gid: str) -> Optional[Game]:
        pass

    @abstractmethod
    def find_games_for_user(self, uid: str) -> Iterable[Game]:
        pass

