from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import tempfile
from app.services.azure_openai import AzureOpenAIService
from app.services.embeddings import EmbeddingsService
from app.services.vector_store import VectorStoreService

router = APIRouter()

# Initialize services
openai_service = AzureOpenAIService()
embeddings_service = EmbeddingsService()
vector_store_service = VectorStoreService(embeddings_service)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Get relevant context from vector store
        last_user_message = next(
            (msg for msg in reversed(request.messages) if msg.role == "user"),
            None
        )
        
        if last_user_message:
            context = await vector_store_service.similarity_search(last_user_message.content)
            context_text = "\n".join([doc.page_content for doc in context])
            
            # Add context to system message
            system_message = {
                "role": "system",
                "content": f"Use the following context to answer the user's question:\n\n{context_text}"
            }
            
            messages = [system_message] + [msg.dict() for msg in request.messages]
        else:
            messages = [msg.dict() for msg in request.messages]
        
        response = openai_service.get_completion(messages)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file.flush()

            # Ingest PDF into vector store
            vector_store_service.ingest_pdf(tmp_file.name)

        return {"message": "PDF successfully ingested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
