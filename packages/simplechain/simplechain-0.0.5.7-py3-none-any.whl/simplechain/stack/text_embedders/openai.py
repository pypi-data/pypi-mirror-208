from typing import List, Dict

import numpy as np
import openai
from pydantic import root_validator

from simplechain.stack.text_embedders.base import TextEmbedder
from simplechain.utils import get_from_dict_or_env


class TextEmbedderOpenAI(TextEmbedder):
    model_name = "text-embedding-ada-002"

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key exists in environment."""
        openai_api_key = get_from_dict_or_env(
            values, "openai_api_key", "OPENAI_API_KEY"
        )
        values["openai_api_key"] = openai_api_key
        openai.api_key = openai_api_key

        return values

    def embed(self, text: str) -> List[float]:
        text = text.replace("\n", " ")
        return openai.Embedding.create(input=[text], model=self.model_name)['data'][0]['embedding']

    def embed_all(self, texts: List[str]) -> List[List[float]]:
        embeddings = openai.Embedding.create(input=texts, model=self.model_name)
        return [embedding['embedding'] for embedding in embeddings['data']]
