from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.schemas import LogoRequest, LogoResponse
from app.services.logo_generator import LogoGenerator
import uuid
import os

router = APIRouter()
logo_generator = LogoGenerator()

@router.post("/generate", response_model=LogoResponse)
async def generate_logo(request: LogoRequest):
    try:
        # Generate the logo
        logo_path, preview_path = logo_generator.generate_logo(request)
        
        # Get the base filename without the directory
        logo_filename = os.path.basename(logo_path)
        preview_filename = os.path.basename(preview_path)
        
        # Generate a unique ID for this request
        generation_id = str(uuid.uuid4())
        
        return LogoResponse(
            logo_url=f"/static/{logo_filename}",
            preview_url=f"/static/{preview_filename}",
            generation_id=generation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{generation_id}")
async def get_logo(generation_id: str):
    try:
        logo_path = f"generated_logos/{generation_id}_logo.png"
        preview_path = f"generated_logos/{generation_id}_preview.png"
        
        if not os.path.exists(logo_path):
            raise HTTPException(status_code=404, detail="Logo not found")
            
        return {
            "logo_url": f"/static/{generation_id}_logo.png",
            "preview_url": f"/static/{generation_id}_preview.png"
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e)) 