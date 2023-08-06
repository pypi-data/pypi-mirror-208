from simplechain.pipeline.module import module


@module("User Input")
def user_input(prompt: str) -> str:
    return input(prompt)
