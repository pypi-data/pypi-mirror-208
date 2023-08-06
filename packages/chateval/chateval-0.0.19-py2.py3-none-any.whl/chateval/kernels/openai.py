from __future__ import annotations

import asyncio
from dataclasses import dataclass
import os
from typing import Optional

import openai

from chateval.kernels.kernel import Kernel, KernelConfig

openai.api_key = os.environ.get("OPENAI_API_KEY")


@dataclass
class OpenAICompletionConfig(KernelConfig):

    model_name: str = "text-curie-001"
    max_tokens: int = 64
    temperature: float = 0.7
    top_p: float = 1
    suffix: str = ""
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    logprobs: float = 1
    n: int = 1
    echo: bool = True
    stop: object = None


class OpenAICompletion(Kernel):
    def __init__(self, config: Optional[OpenAICompletionConfig] = None):
        self.config = config if config is not None else OpenAICompletionConfig()

    def execute(self, code) -> dict[str, str]:

        response = openai.Completion.create(
            model=self.config.model_name,
            prompt=code,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            logprobs=self.config.logprobs,
            frequency_penalty=self.config.frequency_penalty,
            presence_penalty=self.config.presence_penalty,
            n=self.config.n,
            echo=self.config.echo,
            stop=self.config.stop,
        )

        return response["choices"][0]["text"]


@dataclass
class OpenAIChatConfig(KernelConfig):
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 512
    temperature: float = 0
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    n: int = 1


async def dispatch_openai_requests(
    messages_list: list[list[dict[str, str]]],
    model: str,
    temperature: float,
    max_tokens: int,
    top_p: float,
) -> list[str]:
    async_responses = [
        openai.ChatCompletion.acreate(
            model=model,
            messages=x,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        for x in messages_list
    ]
    return await asyncio.gather(*async_responses)


class OpenAIChat(Kernel):
    def __init__(self, config: Optional[OpenAIChatConfig] = None):
        self.config = config if config is not None else OpenAIChatConfig()

    def execute(self, code) -> dict[str, str]:
        response = openai.ChatCompletion.create(
            model=self.config.model_name,
            messages=code,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            frequency_penalty=self.config.frequency_penalty,
            presence_penalty=self.config.presence_penalty,
            n=self.config.n,
        )

        output = response["choices"][0]["message"]["content"]

        return output

    def execute_batch(self, code_list) -> list[dict[str, str]]:

        responses = asyncio.run(
            dispatch_openai_requests(
                messages_list=code_list,
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
            )
        )

        outputs = [
            response["choices"][0]["message"]["content"] for response in responses
        ]
        return outputs
