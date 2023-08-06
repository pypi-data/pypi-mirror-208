from abc import ABC, abstractmethod

from simplechain.stack.text_generators.base import TextGenerator


class TextGeneratorLLM(TextGenerator, ABC):
    model_name: str
    """The name of the model to use."""
    temperature: float = 0.7
    """What sampling temperature to use."""
    max_tokens: int = 256
    """The maximum number of tokens to generate in the completion.
    -1 returns as many tokens as possible given the prompt and
    the models maximal context size."""
    top_p: float = 1
    """Total probability mass of tokens to consider at each step."""
    frequency_penalty: float = 0
    """Penalizes repeated tokens according to frequency."""
    presence_penalty: float = 0

    @abstractmethod
    def generate(self, prompt: str):
        pass