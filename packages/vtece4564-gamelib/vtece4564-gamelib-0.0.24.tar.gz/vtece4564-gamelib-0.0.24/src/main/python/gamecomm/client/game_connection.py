from abc import ABC, abstractmethod
from typing import Optional


class ConnectionClosed(Exception):
    pass


class GameConnection(ABC):

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def send(self, message: str):
        pass

    @abstractmethod
    def recv(self, timeout=None) -> Optional[str]:
        pass


