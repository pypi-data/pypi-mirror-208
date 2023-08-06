from abc import ABC, abstractmethod

from pydantic import BaseModel


class SearchEngine(BaseModel, ABC):

    @abstractmethod
    def search(self, query: str) -> str:
        raise NotImplementedError

