from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.routers import logo
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Logo Generator API",
    description="API for generating custom logos based on brand requirements",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create generated_logos directory if it doesn't exist
os.makedirs("generated_logos", exist_ok=True)

# Mount static files directory at the root level
app.mount("/static", StaticFiles(directory="generated_logos"), name="generated_logos")

# Include routers
app.include_router(
    logo.router,
    prefix=f"/api/{os.getenv('API_VERSION', 'v1')}",
    tags=["Logo Generation"]
)

# Add global error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "The requested resource was not found"}
    )

@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=405,
        content={"detail": "Method not allowed"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc.detail) if hasattr(exc, 'detail') else "Internal server error"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    ) 