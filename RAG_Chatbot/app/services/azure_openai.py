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

    def get_completion(self, messages: list, temperature: float = 0.):
        # Generate the completion  
        response = self.client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=800,
            temperature=temperature
        )
        return response.choices[0].message.content
