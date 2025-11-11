from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat
from app.core.config import settings
from app.services.embeddings import EmbeddingsService
from app.services.vector_store import VectorStoreService

app = FastAPI(
    title="HR Chatbot API",
    description="HR Policies RAG-based chatbot API using Azure OpenAI",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Pre-index PDF files from HR Policies Index folder on startup"""
    try:
        # Get the path to the HR Policies Index folder
        app_dir = Path(__file__).parent
        policies_dir = app_dir / "HR Policies Index"
        
        if not policies_dir.exists():
            print(f"Warning: HR Policies Index folder not found at {policies_dir}")
            return
        
        # Initialize services for pre-indexing
        embeddings_service = EmbeddingsService()
        vector_store_service = VectorStoreService(embeddings_service)
        
        # Pre-index all PDFs in the folder
        print(f"Starting pre-indexing of PDFs from {policies_dir}...")
        vector_store_service.ingest_directory(str(policies_dir))
        
        # Update the vector store service in the chat router
        chat.vector_store_service = vector_store_service
        print("Pre-indexing completed successfully!")
        
    except Exception as e:
        print(f"Error during pre-indexing: {str(e)}")
        # Don't raise - allow the API to start even if indexing fails
        # The user can still upload PDFs manually
