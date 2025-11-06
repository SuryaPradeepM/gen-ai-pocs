import json
import tempfile
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.azure_openai import AzureOpenAIService
from app.services.embeddings import EmbeddingsService
from app.services.session_manager import SessionManager
from app.services.vector_store import VectorStoreService

router = APIRouter()

# Initialize services
openai_service = AzureOpenAIService()
embeddings_service = EmbeddingsService()
vector_store_service = VectorStoreService(embeddings_service)
session_manager = SessionManager()


class ContentItem(BaseModel):
    """Content item with type and text"""
    type: str
    text: str


class ChatMessage(BaseModel):
    """Message in the new format with content as array"""
    role: str
    content: List[ContentItem]


class ChatRequest(BaseModel):
    """Simplified chat request with session_id and user message"""
    session_id: str
    message: str  # User's message text


class ChatResponse(BaseModel):
    """Chat response with message in new format"""
    session_id: str
    message: ChatMessage


def extract_text_from_content(content: List[ContentItem]) -> str:
    """Extract text from content array"""
    return " ".join([item.text for item in content if item.type == "text"])


def create_content_item(text: str) -> ContentItem:
    """Create a content item from text"""
    return ContentItem(type="text", text=text)


def convert_to_azure_format(messages: List[dict]) -> List[dict]:
    """Convert from new format to Azure OpenAI format"""
    azure_messages = []
    for msg in messages:
        if isinstance(msg.get("content"), list):
            # New format: content is array
            text_content = " ".join([
                item.get("text", "") for item in msg["content"]
                if item.get("type") == "text"
            ])
            azure_messages.append({
                "role": msg["role"],
                "content": text_content
            })
        else:
            # Already in Azure format
            azure_messages.append(msg)
    return azure_messages


def convert_from_azure_format(role: str, content: str) -> dict:
    """Convert from Azure OpenAI format to new format"""
    return {
        "role": role,
        "content": [{"type": "text", "text": content}]
    }


async def prepare_messages_async(session_id: str, user_message: str):
    """Prepare messages with context from vector store and session history"""
    # Ensure session exists
    session_manager.ensure_session(session_id)
    # Get session history
    session_history = session_manager.get_session(session_id) or []

    # Get relevant context from vector store
    context = await vector_store_service.similarity_search(user_message)
    context_text = "\n".join([doc.page_content for doc in context])

    # Add context to system message if we have context
    messages = []
    if context_text:
        system_message = {
            "role": "system",
            "content": f"Use the following context to answer the user's question:\n\n{context_text}",
        }
        messages.append(system_message)

    # Add session history (convert to Azure format)
    azure_history = convert_to_azure_format(session_history)
    messages.extend(azure_history)

    # Add current user message
    user_msg = {
        "role": "user",
        "content": user_message
    }
    messages.append(user_msg)

    return messages


@router.post("/session")
async def create_session():
    """Create a new chat session"""
    session_id = session_manager.create_session()
    return {"session_id": session_id}


@router.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint with session management"""
    try:
        # Prepare messages with context and history
        messages = await prepare_messages_async(request.session_id, request.message)

        # Get completion from Azure OpenAI
        response_text = openai_service.get_completion(messages)

        # Convert user message to new format and add to session
        user_message_new_format = convert_from_azure_format("user", request.message)
        session_manager.add_message(request.session_id, user_message_new_format)

        # Convert assistant response to new format and add to session
        assistant_message_new_format = convert_from_azure_format("assistant", response_text)
        session_manager.add_message(request.session_id, assistant_message_new_format)

        # Return response in new format
        return {
            "session_id": request.session_id,
            "message": assistant_message_new_format
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint with session management"""
    try:
        # Prepare messages with context and history
        messages = await prepare_messages_async(request.session_id, request.message)

        # Convert user message to new format and add to session
        user_message_new_format = convert_from_azure_format("user", request.message)
        session_manager.add_message(request.session_id, user_message_new_format)

        full_response = ""

        def generate():
            nonlocal full_response
            # Stream completion chunks
            for chunk in openai_service.stream_completion(messages):
                full_response += chunk
                # Format as Server-Sent Events (SSE) or JSON chunks
                data = json.dumps({"content": chunk})
                yield f"data: {data}\n\n"

            # After streaming completes, add assistant message to session
            assistant_message_new_format = convert_from_azure_format("assistant", full_response)
            session_manager.add_message(request.session_id, assistant_message_new_format)

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session"""
    history = session_manager.get_session(session_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": history}


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    session_manager.delete_session(session_id)
    return {"message": "Session deleted successfully"}


@router.post("/session/{session_id}/clear")
async def clear_session(session_id: str):
    """Clear conversation history for a session"""
    session_manager.clear_session(session_id)
    return {"message": "Session history cleared successfully"}


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file.flush()

            # Ingest PDF into vector store
            vector_store_service.ingest_pdf(tmp_file.name)

        return {"message": "PDF successfully ingested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
