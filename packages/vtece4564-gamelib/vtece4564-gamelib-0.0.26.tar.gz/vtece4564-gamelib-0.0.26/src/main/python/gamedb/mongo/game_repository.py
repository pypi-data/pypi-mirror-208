import logging
from typing import Any, Dict, Iterable, Optional

from pymongo import MongoClient
from pymongo.collection import Collection

from ..game_repository import Game, GameRepository, NoSuchGameError


_GAMES_COLLECTION_NAME = "games"
_ID_KEY = "_id"
_GID_KEY = "gid"
_CUSTOM_KEY = "custom"
_CREATION_DATE_KEY = "creation_date"
_CREATOR_KEY = "creator"
_PLAYERS_KEY = "players"

logger = logging.getLogger(__name__)


class MongoGame(Game):

    @classmethod
    def from_dict(cls, rec: dict) -> "MongoGame":
        return MongoGame(rec.get(_CREATOR_KEY), rec.get(_PLAYERS_KEY), gid=rec.get(_GID_KEY),
                         custom=rec.get(_CUSTOM_KEY), creation_date=rec.get(_CREATION_DATE_KEY))

    def to_dict(self) -> Dict:
        rec = {
            _GID_KEY: self.gid,
            _CREATOR_KEY: self.creator,
            _PLAYERS_KEY: self.players,
            _CREATION_DATE_KEY: self.creation_date,
        }
        if self.custom:
            rec.update({_CUSTOM_KEY: self.custom})
        return rec


class MongoGameRepository(GameRepository):

    def __init__(self, mongo: MongoClient):
        self.games: Collection = mongo.get_default_database().get_collection(_GAMES_COLLECTION_NAME)
        self.games.create_index(_GID_KEY, unique=True)

    def create_game(self, creator: str, players: Iterable[str], custom: Any = None) -> Game:
        game = MongoGame(creator, players, custom=custom)
        game_doc = game.to_dict()
        logger.debug(f"inserting game: {game_doc}")
        doc_id = self.games.insert_one(game_doc).inserted_id
        game_doc = self.games.find_one({_ID_KEY: doc_id})
        return MongoGame.from_dict(game_doc)

    def delete_game(self, gid: str):
        self.games.delete_one({_GID_KEY: gid})

    def find_game(self, gid: str) -> Optional[Game]:
        game_doc = self.games.find_one({_GID_KEY: gid})
        if not game_doc:
            raise NoSuchGameError(f"game {gid} does not exist")
        return MongoGame.from_dict(game_doc)

    def find_games_for_user(self, uid: str) -> Iterable[Game]:
        return [MongoGame.from_dict(game_doc) for game_doc in self.games.find({_PLAYERS_KEY: uid})]

    def replace_game(self, game: Game) -> Game:
        game_doc = self.games.find_one({_GID_KEY: game.gid})
        if game_doc is None:
            raise NoSuchGameError(f"game ID {game.gid} not found")

        db_game = MongoGame.from_dict(game_doc)
        db_game.players = game.players
        db_game.custom = game.custom
        game_doc = db_game.to_dict()
        self.games.replace_one({_GID_KEY: game.gid}, game_doc)
        return db_game
