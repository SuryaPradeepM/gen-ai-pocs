# DB Genie - Hybrid HR Chatbot

A hybrid AI-powered chatbot that combines vector-based document search with SQL database querying and visualization capabilities.

## Features

- **Hybrid Query Routing**: Intelligently routes queries to appropriate backend (documents or database)
- **Document Search**: Vector-based semantic search over PDF policy documents
- **SQL Querying**: Natural language to SQL conversion using LangChain agents
- **Visualizations**: Automatic chart generation (Plotly/Matplotlib/Seaborn)
- **Multi-Database Support**: SQLite, PostgreSQL, MySQL via SQLAlchemy
- **Session Management**: Conversation history tracking
- **Streaming Responses**: Real-time response streaming
- **Dynamic Schema Introspection**: Automatically understands database structure

## Architecture

```Mermaid
User Query
    ↓
Query Router (determines type)
    ↓
┌──────────┬──────────────┬──────────────┐
│  Vector  │   SQL Agent  │ Visualization│
│  Search  │              │   Service    │
└──────────┴──────────────┴──────────────┘
    ↓
Response Formatter
    ↓
User (Text + Charts)
```

## Installation

### 1. Clone Repository

```sh
git clone <your-repo>
cd db-agent-ai
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your Azure OpenAI credentials:

```sh
cp .env.example .env
```

### 4. Create Sample Database

```sh
python scripts/create_sample_db.py
```

### 5. Add PDF Documents

Place your HR policy PDF files in the `HR Policies Index/` folder.

### 6. Run Application

```sh
uvicorn main:app --reload --port 8000
```

## API Endpoints

### Chat Endpoints

- **POST** `/api/v1/session` - Create new chat session
- **POST** `/api/v1/chat` - Send message (returns full response)
- **POST** `/api/v1/chat/stream` - Send message (streaming response)
- **GET** `/api/v1/session/{session_id}/history` - Get conversation history
- **DELETE** `/api/v1/session/{session_id}` - Delete session
- **POST** `/api/v1/session/{session_id}/clear` - Clear session history

### Document Management

- **POST** `/api/v1/upload-pdf` - Upload and index PDF document

### Database Endpoints

- **GET** `/api/v1/database/schema` - Get database schema
- **GET** `/api/v1/database/tables/{table_name}/sample` - Get table sample
- **POST** `/api/v1/query/sql` - Execute raw SQL query (SELECT only)
- **POST** `/api/v1/visualize` - Create visualization from data

### Health Check

- **GET** `/health` - Application health status

## Usage Examples

### Example 1: Policy Question (Vector Search)

```sh
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123",
    "message": "What is the sick leave policy?"
  }'
```

### Example 2: Database Query

```sh
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123",
    "message": "How many employees are in the Engineering department?"
  }'
```

### Example 3: Visualization Request

```sh
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123",
    "message": "Show me a chart of leave distribution by department"
  }'
```

## Query Routing Logic

The system automatically detects query intent:

| Query Type | Keywords | Routed To |
|------------|----------|-----------|
| Policy/Document | "policy", "guideline", "according to" | Vector Store |
| Database Query | "how many", "count", "total", "list all" | SQL Agent |
| Visualization | "show graph", "chart", "plot", "visualize" | SQL + Viz Service |
| Hybrid | Both policy + data keywords | Both systems |

## Database Configuration

### Using SQLite (Default)

```
DATABASE_URL=sqlite:///hr_data.db
```

### Using PostgreSQL

```
DATABASE_URL=postgresql://user:password@localhost:5432/hr_db
```

### Using MySQL

```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hr_db
```

## Troubleshooting

### Issue: "Vector store not initialized"

**Solution**: Ensure PDF files exist in `HR Policies Index/` folder before startup.

### Issue: "Database connection failed"

**Solution**:

1. Check `DATABASE_URL` in `.env`
2. Run `python scripts/create_sample_db.py`
3. Verify database file exists

### Issue: Charts not rendering

**Solution**: Ensure frontend supports HTML rendering for Plotly charts or base64 images.

## Development

### Running Tests

```
pytest tests/
```

### Code Style

```sh
# pip install ruff isort
ruff format app/
isort --profile black app/
```

### Adding New Tables

1. Add tables to your database
2. Restart the application (auto-introspects schema)
3. Query naturally - the agent will discover new tables

## Production Considerations

1. **Database**: Use PostgreSQL instead of SQLite
2. **Session Storage**: Replace in-memory with Redis
3. **Rate Limiting**: Add rate limiting middleware
4. **Authentication**: Implement user authentication
5. **Logging**: Configure structured logging
6. **Monitoring**: Add APM (Application Performance Monitoring)
7. **Caching**: Cache frequently accessed data
8. **Vector Store**: Use persistent FAISS index

## **Production - Deployment Steps**

1. Install dependencies: `pip install -r requirements.txt`
2. Create sample database: `python scripts/create_sample_db.py`
3. Configure `.env` with your Azure OpenAI credentials
4. Add PDF files to `HR Policies Index/` folder
5. Run: `uvicorn main:app --reload`
6. Test endpoints using the examples in README
