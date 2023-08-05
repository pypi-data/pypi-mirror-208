import logging
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from ..game_repository import Game, GameRepository, NoSuchGameError
from .json_db import JsonDatabase

_GID_KEY = "gid"
_CREATION_DATE_KEY = "creation_date"
_CREATOR_KEY = "creator"
_CUSTOM_KEY = "custom"
_PLAYERS_KEY = "players"

logger = logging.getLogger(__name__)


class JsonGame(Game):

    @classmethod
    def from_dict(cls, rec: dict) -> "JsonGame":
        return JsonGame(creator=rec.get(_CREATOR_KEY),
                        players=rec.get(_PLAYERS_KEY),
                        gid=rec.get(_GID_KEY),
                        custom=rec.get(_CUSTOM_KEY),
                        creation_date=datetime.fromisoformat(rec.get(_CREATION_DATE_KEY)))

    def to_dict(self) -> Dict:
        rec = {
            _GID_KEY: self.gid,
            _CREATOR_KEY: self.creator,
            _PLAYERS_KEY: self.players,
            _CREATION_DATE_KEY: self.creation_date.isoformat(),
        }
        if self.custom:
            rec.update({_CUSTOM_KEY: self.custom})
        return rec


class JsonGameRepository(GameRepository):

    def __init__(self, db: JsonDatabase):
        self.db = db

    def create_game(self, creator: str, players: Iterable[str], custom: Any = None) -> Game:
        game = JsonGame(creator, players)
        game_doc = game.to_dict()
        logger.debug(f"inserting game: {game_doc}")

        def do_create(games):
            if game.gid in games:
                raise KeyError(f"duplicate game: {game.gid}")
            games[game.gid] = game_doc

        self.db.with_games(do_create)
        return game

    def delete_game(self, gid: str):
        def do_delete(games):
            if gid in games:
                del games[gid]

        self.db.with_games(do_delete)

    def find_game(self, gid: str) -> Optional[Game]:
        def do_find(games):
            if gid not in games:
                raise NoSuchGameError(f"game {gid} does not exist")
            game_doc = games[gid]
            return JsonGame.from_dict(game_doc)

        return self.db.with_games(do_find)

    def find_games_for_user(self, uid: str) -> Iterable[Game]:
        def do_find(games):
            return [JsonGame.from_dict(game_doc) for game_doc in games.values() if uid in game_doc[_PLAYERS_KEY]]

        return self.db.with_games(do_find)

    def replace_game(self, game: Game) -> Game:
        def do_update(games: Dict[str, Game]):
            if game.gid not in games:
                raise NoSuchGameError(f"game ID {game.gid} not found")
            db_game = JsonGame.from_dict(games[game.gid])
            db_game.players = game.players
            db_game.custom = game.custom
            games[game.gid] = db_game.to_dict()
            return db_game

        return self.db.with_games(do_update)
