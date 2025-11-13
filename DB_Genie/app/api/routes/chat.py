import json
import tempfile
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.azure_openai import AzureOpenAIService
from app.services.query_router import QueryType
from app.services.session_manager import SessionManager

router = APIRouter()

# Initialize services that don't depend on app state
openai_service = AzureOpenAIService()
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
    visualization: Optional[dict] = None  # NEW: For chart data
    query_type: Optional[str] = None  # NEW: For debugging
    data: Optional[List[dict]] = None  # NEW: For structured data results


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
            text_content = " ".join(
                [
                    item.get("text", "")
                    for item in msg["content"]
                    if item.get("type") == "text"
                ]
            )
            azure_messages.append({"role": msg["role"], "content": text_content})
        else:
            # Already in Azure format
            azure_messages.append(msg)
    return azure_messages


def convert_from_azure_format(role: str, content: str) -> dict:
    """Convert from Azure OpenAI format to new format"""
    return {"role": role, "content": [{"type": "text", "text": content}]}


async def prepare_messages_async(request: Request, session_id: str, user_message: str):
    """
    Prepare messages with context from appropriate source(s) based on query routing.
    Returns both messages and routing information.
    """
    # Ensure session exists
    session_manager.ensure_session(session_id)

    # Get session history
    session_history = session_manager.get_session(session_id) or []

    # Get services from app state
    vector_store_service = request.app.state.vector_store_service
    database_service = request.app.state.database_service
    sql_agent_service = request.app.state.sql_agent_service
    query_router_service = request.app.state.query_router_service
    visualization_service = request.app.state.visualization_service

    # Route the query
    routing_info = query_router_service.route_query(
        user_message, has_database=(database_service is not None)
    )

    query_type = routing_info["query_type"]
    needs_visualization = routing_info["needs_visualization"]

    context_text = ""
    sql_result = None
    visualization_data = None

    # Handle different query types
    if query_type == QueryType.VECTOR_SEARCH:
        # Use vector store for policy/document search
        context = await vector_store_service.similarity_search(user_message)
        context_text = "\n\n".join([doc.page_content for doc in context])

    elif query_type == QueryType.SQL_QUERY and sql_agent_service:
        # Use SQL agent for structured data queries
        sql_result = sql_agent_service.query_with_data(user_message)

        if sql_result["success"]:
            context_text = f"Database Query Result:\n{sql_result['answer']}"
        else:
            context_text = f"Database query failed: {sql_result['error']}"

    elif query_type == QueryType.VISUALIZATION and sql_agent_service:
        # Generate visualization from database query
        sql_result = sql_agent_service.query_with_data(user_message)

        if sql_result["success"] and sql_result.get("data"):
            # Create visualization
            viz_result = visualization_service.create_visualization(
                data=sql_result["data"], chart_type="auto", title=user_message
            )

            if viz_result["success"]:
                visualization_data = viz_result
                context_text = f"I've generated a {viz_result['chart_type']} visualization based on your query.\n\nData summary: {sql_result['answer']}"
            else:
                context_text = f"Data retrieved but visualization failed: {viz_result['error']}\n\nData: {sql_result['answer']}"
        else:
            context_text = f"Could not retrieve data for visualization: {sql_result.get('error', 'Unknown error')}"

    elif query_type == QueryType.HYBRID:
        # Combine vector search and SQL query

        # Get policy context
        context = await vector_store_service.similarity_search(user_message)
        policy_context = "\n\n".join([doc.page_content for doc in context])

        # Get SQL data
        if sql_agent_service:
            sql_result = sql_agent_service.query_with_data(user_message)
            sql_context = sql_result["answer"] if sql_result["success"] else ""
        else:
            sql_context = ""

        context_text = (
            f"Policy Context:\n{policy_context}\n\nDatabase Information:\n{sql_context}"
        )

    else:
        # Fallback to vector search
        context = await vector_store_service.similarity_search(user_message)
        context_text = "\n\n".join([doc.page_content for doc in context])

    # Build messages array
    messages = []

    # Add context to system message if available
    if context_text:
        system_message = {
            "role": "system",
            "content": f"You are a helpful HR assistant. Use the following context to answer the user's question:\n\n{context_text}",
        }
        messages.append(system_message)

    # Add session history (convert to Azure format)
    azure_history = convert_to_azure_format(session_history)
    messages.extend(azure_history)

    # Add current user message
    user_msg = {"role": "user", "content": user_message}
    messages.append(user_msg)

    return {
        "messages": messages,
        "query_type": query_type,
        "visualization_data": visualization_data,
        "sql_result": sql_result,
        "needs_visualization": needs_visualization,
    }


@router.post("/session")
async def create_session():
    """Create a new chat session"""
    session_id = session_manager.create_session()
    return {"session_id": session_id}


@router.post("/chat")
async def chat(request: Request, chat_request: ChatRequest):
    """Chat endpoint with session management and hybrid query support"""
    try:
        # Prepare messages with intelligent routing
        prep_result = await prepare_messages_async(
            request, chat_request.session_id, chat_request.message
        )

        messages = prep_result["messages"]
        query_type = prep_result["query_type"]
        visualization_data = prep_result["visualization_data"]
        sql_result = prep_result["sql_result"]

        # Get completion from Azure OpenAI
        response_text = openai_service.get_completion(messages)

        # Convert user message to new format and add to session
        user_message_new_format = convert_from_azure_format(
            "user", chat_request.message
        )
        session_manager.add_message(chat_request.session_id, user_message_new_format)

        # Convert assistant response to new format and add to session
        assistant_message_new_format = convert_from_azure_format(
            "assistant", response_text
        )
        session_manager.add_message(
            chat_request.session_id, assistant_message_new_format
        )

        # Build response
        response = {
            "session_id": chat_request.session_id,
            "message": assistant_message_new_format,
            "query_type": query_type.value
            if hasattr(query_type, "value")
            else str(query_type),
        }

        # Add visualization if available
        if visualization_data:
            response["visualization"] = {
                "type": visualization_data.get("chart_type"),
                "html": visualization_data.get("html"),
                "image_base64": visualization_data.get("image_base64"),
            }

        # Add structured data if available
        if sql_result and sql_result.get("data"):
            response["data"] = sql_result["data"]

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: Request, chat_request: ChatRequest):
    """Streaming chat endpoint with session management"""
    try:
        # Prepare messages with intelligent routing
        prep_result = await prepare_messages_async(
            request, chat_request.session_id, chat_request.message
        )

        messages = prep_result["messages"]
        query_type = prep_result["query_type"]
        visualization_data = prep_result["visualization_data"]

        # Convert user message to new format and add to session
        user_message_new_format = convert_from_azure_format(
            "user", chat_request.message
        )
        session_manager.add_message(chat_request.session_id, user_message_new_format)

        full_response = ""

        def generate():
            nonlocal full_response

            # Send visualization first if available
            if visualization_data:
                viz_data = {
                    "type": "visualization",
                    "data": {
                        "chart_type": visualization_data.get("chart_type"),
                        "html": visualization_data.get("html"),
                        "image_base64": visualization_data.get("image_base64"),
                    },
                }
                yield f"data: {json.dumps(viz_data)}\n\n"

            # Stream completion chunks
            for chunk in openai_service.stream_completion(messages):
                full_response += chunk
                data = json.dumps({"type": "content", "content": chunk})
                yield f"data: {data}\n\n"

            # After streaming completes, add assistant message to session
            assistant_message_new_format = convert_from_azure_format(
                "assistant", full_response
            )
            session_manager.add_message(
                chat_request.session_id, assistant_message_new_format
            )

            # Send completion marker
            completion_data = {
                "type": "complete",
                "query_type": query_type.value
                if hasattr(query_type, "value")
                else str(query_type),
            }
            yield f"data: {json.dumps(completion_data)}\n\n"

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
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    """Upload and index a PDF document"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Get vector store service from app state
        vector_store_service = request.app.state.vector_store_service

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file.flush()

            # Ingest PDF into vector store
            vector_store_service.ingest_pdf(tmp_file.name)

        return {"message": f"PDF '{file.filename}' successfully ingested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# NEW: Database management endpoints


@router.get("/database/schema")
async def get_database_schema(request: Request):
    """Get database schema information"""
    database_service = request.app.state.database_service

    if not database_service:
        raise HTTPException(status_code=503, detail="Database not available")

    return {
        "tables": database_service.get_table_names(),
        "schema": database_service.get_schema_info(),
        "description": database_service.get_schema_description(),
    }


@router.get("/database/tables/{table_name}/sample")
async def get_table_sample(request: Request, table_name: str, limit: int = 5):
    """Get sample data from a specific table"""
    sql_agent_service = request.app.state.sql_agent_service

    if not sql_agent_service:
        raise HTTPException(status_code=503, detail="Database not available")

    result = sql_agent_service.get_table_sample(table_name, limit)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.post("/query/sql")
async def execute_sql_query(request: Request, query: dict):
    """
    Execute a raw SQL query (for advanced users).
    Request body: {"query": "SELECT * FROM table_name LIMIT 10"}
    """
    sql_agent_service = request.app.state.sql_agent_service

    if not sql_agent_service:
        raise HTTPException(status_code=503, detail="Database not available")

    sql_query = query.get("query")
    if not sql_query:
        raise HTTPException(status_code=400, detail="Query parameter required")

    # Security check: Prevent dangerous operations
    dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT"]
    if any(keyword in sql_query.upper() for keyword in dangerous_keywords):
        raise HTTPException(
            status_code=403,
            detail="Dangerous SQL operations not allowed. Only SELECT queries permitted.",
        )

    if not sql_query.strip().upper().startswith("SELECT"):
        raise HTTPException(
            status_code=403,
            detail="Only SELECT queries are allowed in this endpoint.",
        )

    # Potential SQL injection here (Only for debugging/demo)
    result = sql_agent_service.execute_raw_query(sql_query)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/visualize")
async def create_visualization(request: Request, viz_request: dict):
    """
    Create visualization from provided data.
    Request body: {
        "data": [...],
        "chart_type": "bar",
        "title": "Chart Title",
        "x_column": "column1",
        "y_column": "column2"
    }
    """
    visualization_service = request.app.state.visualization_service

    data = viz_request.get("data")
    if not data:
        raise HTTPException(status_code=400, detail="Data required")

    result = visualization_service.create_visualization(
        data=data,
        chart_type=viz_request.get("chart_type", "auto"),
        title=viz_request.get("title"),
        x_column=viz_request.get("x_column"),
        y_column=viz_request.get("y_column"),
        interactive=viz_request.get("interactive", True),
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return result
