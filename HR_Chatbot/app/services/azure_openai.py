from typing import Iterator

from openai import AzureOpenAI

from ..core.config import settings


class AzureOpenAIService:
    def __init__(self):
        # Initialize Azure OpenAI client with key-based authentication
        self.client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )

    def get_completion(
        self,
        messages: list,
        temperature: float = 0.0,
        max_completion_tokens: int = 1600,
    ):
        # Generate the completion
        response = self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            max_completion_tokens=max_completion_tokens,
            # temperature=temperature,
        )
        return response.choices[0].message.content

    def stream_completion(
        self,
        messages: list,
        temperature: float = 0.0,
        max_completion_tokens: int = 1600,
    ) -> Iterator[str]:
        # Generate streaming completion
        completion = self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            max_completion_tokens=max_completion_tokens,
            # temperature=temperature,
            stream=True,
        )

        # Yield content chunks as they arrive
        for chunk in completion:
            if chunk.choices:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
