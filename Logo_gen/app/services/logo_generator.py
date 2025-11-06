import os
import uuid
import requests
from app.models.schemas import LogoRequest
from dotenv import load_dotenv
import base64
from io import BytesIO
from PIL import Image

load_dotenv()

class LogoGenerator:
    def __init__(self):
        self.output_dir = "generated_logos"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Azure OpenAI Configuration
        self.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.api_version = "2024-02-01"  # Latest API version for DALL-E 3
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not all([self.api_base, self.api_key, self.deployment_name]):
            raise ValueError("Missing required Azure OpenAI configuration")

    def _generate_prompt(self, logo_request: LogoRequest) -> str:
        """Generate a detailed prompt for DALL-E based on the logo request"""
        # Start with core brand and style elements
        prompt = f"Create a {logo_request.style.value} style logo for a brand named '{logo_request.brand_name}'"
        
        # Add slogan if provided
        if logo_request.slogan:
            prompt += f" with the slogan '{logo_request.slogan}'"
        
        # Add color scheme
        prompt += f". Use a {logo_request.color_scheme.value} color scheme"
        
        # Add industry context
        if logo_request.industry:
            prompt += f". The brand is in the {logo_request.industry} industry"
        
        # Add target audience consideration
        prompt += f". The logo should appeal to {logo_request.target_audience.value}"
        
        # Add usage context
        prompt += f". It will be primarily used for {logo_request.usage_context.value}"
        
        # Add preferred symbols if specified
        if logo_request.preferred_symbols:
            symbols_str = ", ".join(logo_request.preferred_symbols)
            prompt += f". Incorporate these elements: {symbols_str}"
        
        # Add elements to avoid
        if logo_request.avoid_elements:
            avoid_str = ", ".join(logo_request.avoid_elements)
            prompt += f". Avoid using these elements: {avoid_str}"
        
        # Add brand values
        if logo_request.brand_values:
            values_str = ", ".join(logo_request.brand_values)
            prompt += f". The logo should convey these brand values: {values_str}"
        
        # Add competitor differentiation
        if logo_request.competitor_differentiation:
            prompt += f". {logo_request.competitor_differentiation}"
        
        # Add font style preference
        if logo_request.font_style:
            prompt += f". Use a {logo_request.font_style} font style"
        
        # Add simplicity requirement
        if logo_request.maintain_simplicity:
            prompt += ". Prioritize simplicity and scalability in the design"
        
        # Add additional notes if provided
        if logo_request.additional_notes:
            prompt += f". Additional requirements: {logo_request.additional_notes}"
        
        # Add final standard requirements
        prompt += (". The logo should be professional, memorable, and work well in both "
                  "digital and print formats. Generate one logo centered on a pure white background.")
        
        return prompt

    def _call_dalle_api(self, prompt: str) -> str:
        """Call Azure OpenAI DALL-E API to generate the image"""
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        body = {
            "prompt": prompt,
            "size": "1024x1024",
            "n": 1,
            "quality": "hd",
            "style": "vivid"
        }
        
        url = f"{self.api_base}openai/deployments/{self.deployment_name}/images/generations?api-version={self.api_version}"
        
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                return result["data"][0]["url"]
            else:
                raise Exception("No image URL in the response")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling DALL-E API: {str(e)}")

    def _download_and_save_image(self, image_url: str, generation_id: str) -> tuple[str, str]:
        """Download the image from the URL and save it locally"""
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Save original logo
        logo_path = f"{self.output_dir}/{generation_id}_logo.png"
        preview_path = f"{self.output_dir}/{generation_id}_preview.png"
        
        # Save the original image
        with open(logo_path, "wb") as f:
            f.write(response.content)
        
        # Create and save a preview version (you could resize or modify it)
        img = Image.open(BytesIO(response.content))
        preview_size = (512, 512)  # Smaller size for preview
        img.thumbnail(preview_size)
        img.save(preview_path)
        
        return logo_path, preview_path

    def generate_logo(self, logo_request: LogoRequest) -> tuple[str, str]:
        """Generate a logo using DALL-E based on the request parameters"""
        try:
            # Create a unique ID for this generation
            generation_id = str(uuid.uuid4())
            
            # Generate the prompt for DALL-E
            prompt = self._generate_prompt(logo_request)
            
            # Call DALL-E API to generate the image
            image_url = self._call_dalle_api(prompt)
            
            # Download and save the image
            logo_path, preview_path = self._download_and_save_image(image_url, generation_id)
            
            return logo_path, preview_path
            
        except Exception as e:
            raise Exception(f"Failed to generate logo: {str(e)}")