import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat
from app.core.config import settings
from app.services.database import DatabaseService
from app.services.embeddings import EmbeddingsService
from app.services.query_router import QueryRouterService
from app.services.sql_agent import SQLAgentService
from app.services.vector_store import VectorStoreService
from app.services.visualization import VisualizationService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DB Genie",
    description="A hybrid AI agent to retrieve data from SQL databases and documents, answer questions, and generate visualizations",
    version="2.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    try:
        logger.info("Starting application initialization...")

        # Initialize embeddings service
        embeddings_service = EmbeddingsService()

        # Initialize vector store service
        vector_store_service = VectorStoreService(embeddings_service)

        # Pre-index PDF files if folder exists
        app_dir = Path(__file__).parent
        policies_dir = (
            app_dir / settings.HR_POLICIES_FOLDER
        )  # FIX: Use config instead of hardcoded path

        if policies_dir.exists():
            logger.info(f"Pre-indexing PDFs from {policies_dir}...")
            try:
                vector_store_service.ingest_directory(str(policies_dir))
                logger.info("PDF pre-indexing completed successfully")
            except Exception as e:
                logger.error(f"Error during PDF pre-indexing: {str(e)}")
        else:
            logger.warning(f"HR Policies folder not found at {policies_dir}")

        # Initialize database service if enabled
        database_service = None
        sql_agent_service = None

        if settings.ENABLE_DATABASE:
            try:
                logger.info(
                    f"Initializing database connection: {settings.DATABASE_URL}"
                )
                database_service = DatabaseService(settings.DATABASE_URL)

                # Test connection
                if database_service.test_connection():
                    logger.info("Database connection successful")

                    # Log schema information
                    table_names = database_service.get_table_names()
                    logger.info(f"Found tables: {table_names}")

                    # Initialize SQL agent
                    sql_agent_service = SQLAgentService(database_service)
                    logger.info("SQL Agent initialized successfully")
                else:
                    logger.error("Database connection test failed")

            except Exception as e:
                logger.error(f"Database initialization error: {str(e)}")
                logger.warning("Continuing without database support")

        # Initialize visualization service
        visualization_service = VisualizationService()

        # Initialize query router
        query_router_service = QueryRouterService()

        # Store services in app state for access by routes
        app.state.vector_store_service = vector_store_service
        app.state.database_service = database_service
        app.state.sql_agent_service = sql_agent_service
        app.state.visualization_service = visualization_service
        app.state.query_router_service = query_router_service
        app.state.embeddings_service = embeddings_service

        logger.info("Application initialization completed successfully!")

    except Exception as e:
        logger.error(f"Critical error during startup: {str(e)}")
        # Don't raise - allow API to start in degraded mode


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database_enabled": settings.ENABLE_DATABASE,
        "has_database": app.state.database_service is not None,
        "has_vector_store": app.state.vector_store_service is not None,
    }
