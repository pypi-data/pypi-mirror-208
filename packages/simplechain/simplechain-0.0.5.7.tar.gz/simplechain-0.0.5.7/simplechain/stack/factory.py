
from simplechain.stack.text_embedders.base import TextEmbedder
from simplechain.stack.text_generators.base import TextGenerator
from simplechain.stack.vector_databases.base import VectorDatabase

class TextEmbedderFactory:
    @classmethod
    def create(cls, name: str, **kwargs) -> TextEmbedder:
        if name == "openai":
            from simplechain.stack.text_embedders.openai import TextEmbedderOpenAI
            return TextEmbedderOpenAI(**kwargs)
        elif name == "ai21":
            from simplechain.stack.text_embedders.ai21 import TextEmbedderAI21
            return TextEmbedderAI21(**kwargs)
        else:
            raise ValueError(f"Invalid name: {name}.")

    @classmethod
    def createOpenAI(cls, **kwargs) -> TextEmbedder:
        from simplechain.stack.text_embedders.openai import TextEmbedderOpenAI
        return TextEmbedderOpenAI(**kwargs)


class VectorDatabaseFactory:
    @classmethod
    def create(cls, name: str, *args, **kwargs) -> VectorDatabase:
        if name == "annoy":
            from simplechain.stack.vector_databases.annoy_vd import Annoy
            return Annoy(*args, **kwargs)
        else:
            raise ValueError(f"Invalid name: {name}.")





class TextGeneratorFactory:
    @classmethod
    def create(cls, name: str, **kwargs) -> TextGenerator:
        if name == "openai":
            from simplechain.stack.text_generators.llms.openai import TextGeneratorOpenAI
            return TextGeneratorOpenAI(**kwargs)
        elif name == "ai21":
            from simplechain.stack.text_generators.llms.ai21 import TextGeneratorAI21
            return TextGeneratorAI21(**kwargs)
        else:
            raise ValueError(f"Invalid name: {name}.")
