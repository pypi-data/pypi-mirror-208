from typing import Tuple, List, Callable, Union

import numpy as np

from simplechain.pipeline.module import module
from simplechain.stack import TextGenerator, TextEmbedder
from simplechain.stack.vector_databases.base import VectorDatabase

@module("Prompt Template")
def prompt_template(prompt: str, **kwargs):
    return prompt.format(kwargs)

@module("Generate Module")
def generate(prompt: str, text_generator: TextGenerator):
    return text_generator.generate(prompt).strip()

@module("Embed")
def embed(prompt: Union[list[str], str], text_embedder: TextEmbedder) -> Union[list[np.ndarray], np.ndarray]:
    return text_embedder.embed(prompt)

@module("Nearest Neighbors")
def nearest_neighbors(embedding: np.ndarray, vector_database: VectorDatabase) -> List[Tuple[str, float]]:
    return vector_database.get_nearest_neighbors(embedding)
