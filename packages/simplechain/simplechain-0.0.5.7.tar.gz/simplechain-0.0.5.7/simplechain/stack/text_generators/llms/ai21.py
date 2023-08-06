from typing import Dict

from pydantic import root_validator

from simplechain.stack.text_generators.llms.llm import TextGeneratorLLM
from simplechain.utils import get_from_dict_or_env

import ai21


class TextGeneratorAI21(TextGeneratorLLM):
    """OpenAI text generator."""
    model_name = "j2-grande-instruct"

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key exists in environment."""

        ai21_api_key = get_from_dict_or_env(
            values, "ai21_api_key", "AI21_API_KEY"
        )
        values["ai21_api_key"] = ai21_api_key
        ai21.api_key = ai21_api_key

        return values

    def generate(self, prompt: str):
        response = ai21.Completion.execute(
            model=self.model_name,
            prompt=prompt,
            numResults=1,
            maxTokens=self.max_tokens,
            temperature=self.temperature,
            topKReturn=0,
            topP=self.top_p,
            countPenalty={
                "scale": 0,
                "applyToNumbers": False,
                "applyToPunctuations": False,
                "applyToStopwords": False,
                "applyToWhitespaces": False,
                "applyToEmojis": False
            },
            frequencyPenalty={
                "scale": 0,
                "applyToNumbers": False,
                "applyToPunctuations": False,
                "applyToStopwords": False,
                "applyToWhitespaces": False,
                "applyToEmojis": False
            },
            presencePenalty={
                "scale": 0,
                "applyToNumbers": False,
                "applyToPunctuations": False,
                "applyToStopwords": False,
                "applyToWhitespaces": False,
                "applyToEmojis": False
            },
            stopSequences=[]
        )

        if 'completions' not in response or response['completions'][0]['data']['text'] == '' or \
                response['completions'][0]['data']['text'].isspace():
            return None

        return response['completions'][0]['data']['text'].strip()
