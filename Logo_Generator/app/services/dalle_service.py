from openai import AzureOpenAI
import json

from ..config import Settings


class DalleService:
    def __init__(self, settings: Settings):
        self.client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            api_version="2023-12-01-preview",
        )
        self.deployment_name = settings.azure_openai_deployment_name

    async def generate_logo(self, prompt: str) -> str:
        try:
            response = self.client.images.generate(
                model=self.deployment_name,
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            # response_data = json.loads(response.model_dump_json())
            # image_url = response_data["data"][0]["url"]
            image_url = response.data[0].url
            return image_url
        except Exception as exp:
            raise Exception(f"Error generating logo: {str(exp)}")

    def create_prompt(
        self,
        company_name: str,
        industry: str,
        style: str,
        colors: str,
        additional_details: str = None,
    ) -> str:
        prompt = f"Create a professional and creative logo for a {industry} company named '{company_name}'. "
        prompt += f"The logo should be in {style} style with {colors} colors. "

        if additional_details:
            prompt += f"Additional Details: {additional_details}. "

        prompt += (
            "The logo should be simple, memorable, and work well in both small and large sizes. "
            "Generate it on a clean white background. Make sure to generate only a logo"
            )

        return prompt
