import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from sqlalchemy import MetaData, Table, create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Database abstraction layer supporting multiple database backends.
    Performs dynamic schema introspection at initialization.
    """

    def __init__(self, database_url: str):
        """
        Initialize database connection with connection pooling.

        Args:
            database_url: Database connection string (e.g., 'sqlite:///./hr_data.db')
        """
        self.database_url = database_url

        # Configure engine based on database type
        if database_url.startswith("sqlite"):
            # SQLite-specific configuration
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False,  # Set to True for SQL query debugging
            )
        else:
            # PostgreSQL/MySQL configuration
            self.engine = create_engine(
                database_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # Verify connections before using
                echo=False,
            )

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.metadata = MetaData()
        self.schema_info: Dict[str, Dict[str, Any]] = {}

        # Introspect schema on initialization
        self._introspect_schema()

    def _introspect_schema(self):
        """
        Dynamically introspect database schema to understand table structure.
        Stores table names, columns, data types, and relationships.
        """
        try:
            inspector = inspect(self.engine)
            table_names = inspector.get_table_names()

            logger.info(f"Found {len(table_names)} tables in database: {table_names}")

            for table_name in table_names:
                columns = inspector.get_columns(table_name)
                primary_keys = inspector.get_pk_constraint(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)

                self.schema_info[table_name] = {
                    "columns": {
                        col["name"]: {
                            "type": str(col["type"]),
                            "nullable": col["nullable"],
                            "default": col.get("default"),
                        }
                        for col in columns
                    },
                    "primary_keys": primary_keys.get("constrained_columns", []),
                    "foreign_keys": foreign_keys,
                    "column_list": [col["name"] for col in columns],
                }

            logger.info(
                f"Schema introspection complete. Tables: {list(self.schema_info.keys())}"
            )

        except Exception as e:
            logger.error(f"Error during schema introspection: {str(e)}")
            raise

    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions with automatic cleanup.

        Usage:
            with db_service.get_session() as session:
                result = session.execute(query)
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()

    def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as list of dictionaries.

        Args:
            query: SQL query string
            params: Optional query parameters for parameterized queries

        Returns:
            List of dictionaries representing query results
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})

                # Convert result to list of dicts
                if result.returns_rows:
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in result.fetchall()]
                else:
                    return []

        except Exception as e:
            logger.error(f"Query execution error: {str(e)}\nQuery: {query}")
            raise

    def get_schema_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get complete schema information for all tables.

        Returns:
            Dictionary with table names as keys and schema details as values
        """
        return self.schema_info

    def get_table_names(self) -> List[str]:
        """Get list of all table names in the database."""
        return list(self.schema_info.keys())

    def get_table_schema(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get schema information for a specific table.

        Args:
            table_name: Name of the table

        Returns:
            Dictionary with column information or None if table doesn't exist
        """
        return self.schema_info.get(table_name)

    def get_schema_description(self) -> str:
        """
        Generate a human-readable description of the database schema.
        Useful for providing context to LLMs.

        Returns:
            Formatted string describing all tables and columns
        """
        description_parts = []

        for table_name, table_info in self.schema_info.items():
            columns_desc = []
            for col_name, col_info in table_info["columns"].items():
                pk_marker = (
                    " (PRIMARY KEY)" if col_name in table_info["primary_keys"] else ""
                )
                columns_desc.append(f"  - {col_name}: {col_info['type']}{pk_marker}")

            table_desc = f"Table: {table_name}\n" + "\n".join(columns_desc)
            description_parts.append(table_desc)

        return "\n\n".join(description_parts)

    def test_connection(self) -> bool:
        """
        Test database connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
