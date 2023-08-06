from abc import ABC, abstractmethod

from pydantic import BaseModel


class TextGenerator(BaseModel, ABC):
    @abstractmethod
    def generate(self, prompt: str):
        pass