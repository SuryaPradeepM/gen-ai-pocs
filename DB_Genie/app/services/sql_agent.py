import logging
from typing import Any, Dict

from langchain_classic.agents.agent_types import AgentType
from langchain_community.agent_toolkits.sql.base import create_sql_agent
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

        # FIX: Initialize Azure OpenAI LLM WITHOUT 'stop' parameter support
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=1,  # Deterministic for SQL generation
            max_tokens=1500,
            model_kwargs={
                "stop": None  # FIX: Explicitly set stop to None to prevent it from being sent
            },
        )

        # FIX: Override the default stop parameter behavior
        # Some Azure OpenAI models don't support 'stop' parameter
        original_bind_tools = (
            self.llm.bind_tools if hasattr(self.llm, "bind_tools") else None
        )

        # Create SQL agent with fixed configuration
        try:
            self.agent = create_sql_agent(
                llm=self.llm,
                db=self.langchain_db,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,  # Set to False in production
                handle_parsing_errors=True,
                max_iterations=5,
                max_execution_time=30,  # 30 seconds timeout
                # FIX: Pass agent_kwargs to override default stop sequences
                agent_executor_kwargs={
                    "handle_parsing_errors": True,
                    "return_intermediate_steps": False,
                },
            )
            logger.info("SQL Agent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SQL Agent: {str(e)}")
            raise

    def query(self, natural_language_query: str) -> Dict[str, Any]:
        """
        Convert natural language query to SQL and execute it.

        Args:
            natural_language_query: User's question in natural language

        Returns:
            Dictionary containing:
                - success: bool
                - data: query results (list of dicts)
                - answer: formatted answer string
                - error: error message (if failed)
        """
        try:
            # Add schema context to improve query accuracy
            schema_desc = self.database_service.get_schema_description()
            # TODO: Add dedent for better formatting of prompts
            enhanced_query = f"""
You have access to a database with the following schema:

{schema_desc}

User Question: {natural_language_query}

Please answer the question by querying the database. Provide a clear, concise answer.
"""

            # FIX: Execute agent with explicit config to avoid 'stop' parameter
            result = self.agent.invoke(
                {"input": enhanced_query},
                config={"callbacks": [], "tags": [], "metadata": {}},
            )

            # Extract output
            output = result.get("output", "")

            return {
                "success": True,
                "answer": output,
                "data": None,  # Agent handles formatting internally
                "error": None,
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"SQL Agent query error: {error_msg}")

            # FIX: Provide more helpful error message
            if "'stop'" in error_msg and "not supported" in error_msg:
                error_msg = "Model doesn't support 'stop' parameter. Please check your Azure OpenAI deployment configuration."

            return {"success": False, "answer": None, "data": None, "error": error_msg}

    def query_with_data(self, natural_language_query: str) -> Dict[str, Any]:
        """
        Execute query and return raw data for visualization.

        Args:
            natural_language_query: User's question in natural language

        Returns:
            Dictionary with success status, data, and generated SQL
        """
        try:
            # Use a simpler approach: generate SQL and execute directly
            # This avoids the agent's stop parameter issue

            schema_desc = self.database_service.get_schema_description()

            # Ask the LLM to generate SQL
            from app.services.azure_openai import AzureOpenAIService

            openai_service = AzureOpenAIService()

            sql_generation_prompt = f"""
You are a SQL expert. Generate a valid SELECT query for the following question.

Database Schema:
{schema_desc}

Question: {natural_language_query}

Return ONLY the SQL query, nothing else. No explanations.
"""

            messages = [
                {"role": "system", "content": "You generate SQL queries."},
                {"role": "user", "content": sql_generation_prompt},
            ]

            sql_query = openai_service.get_completion(messages, temperature=1)

            # Clean the SQL
            sql_query = sql_query.strip()
            sql_query = sql_query.replace("``````", "").strip()

            # Execute the SQL
            data = self.database_service.execute_query(sql_query)

            # Generate answer
            answer_prompt = f"""
Based on this query result, answer the user's question concisely.

Question: {natural_language_query}
Data: {data[:5] if len(data) > 5 else data}

Provide a clear, short answer:
"""

            messages = [
                {"role": "system", "content": "You explain database results clearly."},
                {"role": "user", "content": answer_prompt},
            ]

            answer = openai_service.get_completion(messages, temperature=1)

            return {
                "success": True,
                "data": data,
                "answer": answer,
                "sql_query": sql_query,
                "error": None,
            }

        except Exception as e:
            logger.error(f"SQL query with data error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "answer": None,
                "sql_query": None,
                "error": str(e),
            }

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
            # Validate table exists
            if table_name not in self.database_service.get_table_names():
                raise ValueError(f"Table '{table_name}' does not exist")

            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            results = self.database_service.execute_query(query)

            return {
                "success": True,
                "table_name": table_name,
                "sample_data": results,
                "row_count": len(results),
                "error": None,
            }

        except Exception as e:
            logger.error(f"Error fetching table sample: {str(e)}")
            return {
                "success": False,
                "table_name": table_name,
                "sample_data": None,
                "row_count": 0,
                "error": str(e),
            }
