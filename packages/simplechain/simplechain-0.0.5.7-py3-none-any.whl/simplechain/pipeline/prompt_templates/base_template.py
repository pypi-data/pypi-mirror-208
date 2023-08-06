from typing import List

from simplechain.pipeline.module import module


@module("Base Template")
def base_template(prompt: str) -> str:
    """Base template for prompt templates."""
    return prompt






