from abc import ABC, abstractmethod
from typing import List


from pydantic import BaseModel


class TextEmbedder(BaseModel, ABC):
    @abstractmethod
    def embed(self, text:  str) -> List[float]:
        pass

    @abstractmethod
    def embed_all(self, texts: List[str]) -> List[List[float]]:
        pass


