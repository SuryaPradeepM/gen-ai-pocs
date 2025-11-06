# Note: DALL-E 3 requires version 1.0.0 of the openai-python library or later
import json
import os

from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2024-02-01",
    azure_endpoint="https://azure-openai-temp.openai.azure.com/",
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)

result = client.images.generate(
    model="dall-e-3",  # the name of your DALL-E 3 deployment
    prompt="<the user's prompt>",
    n=1,
)

image_url = json.loads(result.model_dump_json())["data"][0]["url"]
