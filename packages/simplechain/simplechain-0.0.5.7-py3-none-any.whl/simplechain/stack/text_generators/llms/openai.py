from typing import Dict

import openai
from pydantic import root_validator

from simplechain.stack.text_generators.llms.llm import TextGeneratorLLM
from simplechain.utils import get_from_dict_or_env


class TextGeneratorOpenAI(TextGeneratorLLM):
    """OpenAI text generator."""
    model_name = "text-davinci-003"

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key exists in environment."""
        openai_api_key = get_from_dict_or_env(
            values, "openai_api_key", "OPENAI_API_KEY"
        )
        values["openai_api_key"] = openai_api_key
        openai.api_key = openai_api_key

        return values

    def generate(self, prompt: str):
        response = openai.Completion.create(
            model=self.model_name,
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=[" Human:", " AI:"]
        )
        return response.choices[0].text
