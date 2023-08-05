import json
import os
import shutil
from threading import Lock
from typing import Any, Callable, Dict

_GAMES_KEY = "games"
_USERS_KEY = "users"


class JsonDatabase:

    def __init__(self, path: str):
        self.path = path
        dir = os.path.dirname(path)
        if dir:
            os.makedirs(dir, exist_ok=True)
        base, ext = os.path.splitext(self.path)
        self.backup_path = f"{base}_backup{ext}"
        self._data = None
        self._lock = Lock()

    def _load_file(self):
        try:
            with open(self.path, "r") as input_file:
                self._data = json.load(input_file)
        except FileNotFoundError:
            self._data = {
                _USERS_KEY: {},
                _GAMES_KEY: {},
            }

    def _save_file(self):
        try:
            shutil.copyfile(self.path, self.backup_path)
        except FileNotFoundError:
            pass

        with open(self.path, "w+") as output_file:
            json.dump(self._data, output_file, indent=2)

    def _with_data(self, key: str, op: Callable[[Dict], Any]) -> Any:
        with self._lock:
            if self._data is None:
                self._load_file()
            result = op(self._data[key])
            self._save_file()
            return result

    def with_games(self, op: Callable[[Dict], Any]) -> Any:
        return self._with_data(_GAMES_KEY, op)

    def with_users(self, op: Callable[[Dict], Any]) -> Any:
        return self._with_data(_USERS_KEY, op)
