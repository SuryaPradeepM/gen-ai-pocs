import logging
from typing import Any, Dict, List, Optional

from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain_community.utilities import SQLDatabase
from langchain_openai import AzureChatOpenAI

from app.core.config import settings
from app.services.database import DatabaseService

logger = logging.getLogger(__name__)


class SQLAgentService:
    """
    Service for natural language to SQL query conversion using LangChain SQL agents.
    Handles complex queries and returns structured results.
    """

    def __init__(self, database_service: DatabaseService):
        """
        Initialize SQL agent with database connection and LLM.

        Args:
            database_service: Initialized DatabaseService instance
        """
        self.database_service = database_service

        # Create LangChain SQLDatabase wrapper
        self.langchain_db = SQLDatabase(engine=database_service.engine)

        # Initialize Azure OpenAI LLM for agent
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=0,  # Deterministic for SQL generation
            max_tokens=1500,
        )

        # Create SQL toolkit and agent
        self.toolkit = SQLDatabaseToolkit(db=self.langchain_db, llm=self.llm)

        self.agent = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,  # Set to False in production
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="generate",
        )

        logger.info("SQL Agent initialized successfully")

    def query(self, natural_language_query: str) -> Dict[str, Any]:
        """
        Convert natural language query to SQL and execute it.

        Args:
            natural_language_query: User's question in natural language

        Returns:
            Dictionary containing:
                - success: bool
                - data: query results (list of dicts)
                - sql_query: generated SQL query (if available)
                - error: error message (if failed)
        """
        try:
            # Add schema context to the query
            schema_desc = self.database_service.get_schema_description()
            enhanced_query = f"""
            Database Schema:
            {schema_desc}
            
            User Question: {natural_language_query}
            
            Please provide a clear answer based on the database. If the query requires data retrieval, 
            execute the appropriate SQL query and format the results in a readable way.
            """

            # Execute agent
            result = self.agent.invoke({"input": enhanced_query})

            # Extract output
            output = result.get("output", "")

            return {
                "success": True,
                "answer": output,
                "data": None,  # Agent handles formatting
                "error": None,
            }

        except Exception as e:
            logger.error(f"SQL Agent query error: {str(e)}")
            return {"success": False, "answer": None, "data": None, "error": str(e)}

    def execute_raw_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute a raw SQL query directly (for advanced users or debugging).

        Args:
            sql_query: Raw SQL query string

        Returns:
            Dictionary with success status and results
        """
        try:
            results = self.database_service.execute_query(sql_query)

            return {
                "success": True,
                "data": results,
                "row_count": len(results),
                "error": None,
            }

        except Exception as e:
            logger.error(f"Raw query execution error: {str(e)}")
            return {"success": False, "data": None, "row_count": 0, "error": str(e)}

    def get_table_sample(self, table_name: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get sample rows from a table.

        Args:
            table_name: Name of the table
            limit: Number of rows to retrieve

        Returns:
            Dictionary with sample data
        """
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            results = self.database_service.execute_query(query)

            return {
                "success": True,
                "table_name": table_name,
                "sample_data": results,
                "error": None,
            }

        except Exception as e:
            logger.error(f"Error fetching table sample: {str(e)}")
            return {
                "success": False,
                "table_name": table_name,
                "sample_data": None,
                "error": str(e),
            }
