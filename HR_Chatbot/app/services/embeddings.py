from openai import AzureOpenAI

from ..core.config import settings


class EmbeddingsService:
    def __init__(self):
        # Initialize Azure OpenAI client with key-based authentication
        self.client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version="2023-05-15",
        )

    def get_embeddings(self, text: str):
        response = self.client.embeddings.create(
            model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME, input=text
        )
        return response.data[0].embedding
