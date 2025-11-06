from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.models.request_models import LogoRequest
from app.services.dalle_service import DalleService

app = FastAPI(title="Logo Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DALL-E service
settings = get_settings()
dalle_service = DalleService(settings)


@app.post("/generate-logo")
async def generate_logo(request: LogoRequest):
    try:
        logger.info(f"Generating logo for company: {request.company_name}")
        # Create the prompt for DALL-E
        prompt = dalle_service.create_prompt(
            company_name=request.company_name,
            industry=request.industry,
            style=request.style,
            colors=request.colors,
            additional_details=request.additional_details,
        )
        logger.debug(f"Generated prompt: {prompt}")

        # Generate the logo
        image_url = await dalle_service.generate_logo(prompt)
        logger.info(f"Successfully generated logo for {request.company_name}")

        return {"status": "success", "image_url": image_url, "prompt": prompt}
    except Exception as exp:
        logger.error(f"Error generating logo: {str(exp)}")
        raise HTTPException(status_code=500, detail=str(exp))


@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint called")
    return {"status": "healthy"}


@app.get("/")
async def health_check():
    logger.debug("Root endpoint called")
    return {"status": "App Running"}
