import logging
import re
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from sqlalchemy import MetaData, Table, create_engine, inspect, text
from sqlalchemy.exc import OperationalError
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
            database_url: Database connection string (e.g., 'sqlite:///hr_data.db')
        """
        self.database_url = database_url

        # Configure engine based on database type
        if database_url.startswith("sqlite"):
            # SQLite-specific configuration
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=True,  # Set to True for SQL query debugging
            )
        else:
            # PostgreSQL/MySQL configuration
            self.engine = create_engine(
                database_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # Verify connections before using
                echo=True,
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
            # Quick sanity check for sqlite files: if the underlying file is empty
            # it's likely a placeholder/zero-byte file and will contain no tables.
            if self.database_url.startswith("sqlite"):
                # extract path after scheme (support sqlite:///relative/path and sqlite:////absolute on *nix/windows)
                path_part = self.database_url
                if path_part.startswith("sqlite:///"):
                    path_part = path_part[len("sqlite:///") :]
                elif path_part.startswith("sqlite://"):
                    path_part = path_part[len("sqlite://") :]

                try:
                    from pathlib import Path

                    db_file = Path(path_part)
                    # If path is not absolute, resolve relative to project root
                    if not db_file.is_absolute():
                        db_file = (Path(__file__).parent.parent / db_file).resolve()

                    if db_file.exists() and db_file.stat().st_size == 0:
                        msg = (
                            f"SQLite database file '{db_file}' exists but is empty (0 bytes). "
                            "This explains why no tables were found. \n"
                            "If you expect sample data, run 'python app/scripts/create_sample_db.py' "
                            "to populate the database or point DATABASE_URL to a valid DB file."
                        )
                        logger.error(msg)
                        # raise a helpful error so callers can see what's wrong
                        raise RuntimeError(msg)
                except Exception:
                    # Non-fatal: fall back to normal introspection below and let inspector raise if needed
                    logger.debug(
                        "Could not stat sqlite file for quick sanity check",
                        exc_info=True,
                    )

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
    def get_session(self) -> Generator[Session, None, None]:
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

        except OperationalError as oe:
            # Handle common SQLite issues for AI-generated SQL (e.g. CONCAT function missing)
            msg = str(oe)
            logger.warning(
                f"OperationalError executing query: {msg}\nOriginal query: {query}"
            )

            # If CONCAT is used (common in MySQL/Postgres SQL generated by LLMs), transform it
            # into SQLite-compatible string concatenation using '||' and retry once.
            if "no such function: CONCAT" in msg or "CONCAT(" in query.upper():
                try:
                    transformed = self._transform_concat_to_sqlite(query)
                    logger.info(
                        f"Retrying transformed query for SQLite:\n{transformed}"
                    )
                    with self.get_session() as session:
                        result = session.execute(text(transformed), params or {})
                        if result.returns_rows:
                            columns = result.keys()
                            return [
                                dict(zip(columns, row)) for row in result.fetchall()
                            ]
                        else:
                            return []
                except Exception as e2:
                    logger.error(
                        f"Retry after transforming CONCAT failed: {str(e2)}\nTransformed query: {transformed}"
                    )
                    raise

            # For other operational errors, log and re-raise to let higher layers handle them
            logger.error(f"Query execution OperationalError: {msg}\nQuery: {query}")
            raise

        except Exception as e:
            logger.error(f"Query execution error: {str(e)}\nQuery: {query}")
            raise

    def _transform_concat_to_sqlite(self, query: str) -> str:
        """
        Transform CONCAT(a, b, c, ...) into (a || b || c || ...), respecting quoted strings.

        This is a lightweight, defensive transform intended to handle common AI-generated
        SQL that uses CONCAT (MySQL/Postgres style) when running against SQLite.

        It will replace occurrences of CONCAT(...) even when there are spaces, newlines,
        or simple quoted literals inside. It is not a full SQL parser, but suffices for
        typical CONCAT usages like CONCAT(e.first_name, ' ', e.last_name).
        """

        def _split_args(argstr: str) -> List[str]:
            # Split on commas that are not inside single or double quotes or nested parens
            args: List[str] = []
            cur = []
            in_single = False
            in_double = False
            depth = 0
            for ch in argstr:
                if ch == "'" and not in_double:
                    in_single = not in_single
                    cur.append(ch)
                    continue
                if ch == '"' and not in_single:
                    in_double = not in_double
                    cur.append(ch)
                    continue
                if ch == "(" and not in_single and not in_double:
                    depth += 1
                elif ch == ")" and not in_single and not in_double:
                    depth -= 1

                if ch == "," and depth == 0 and not in_single and not in_double:
                    args.append("".join(cur).strip())
                    cur = []
                else:
                    cur.append(ch)

            if cur:
                args.append("".join(cur).strip())

            return args

        # regex to find CONCAT(...), case-insensitive
        pattern = re.compile(r"CONCAT\s*\((.*?)\)", flags=re.IGNORECASE | re.DOTALL)

        def _repl(match: re.Match) -> str:
            inner = match.group(1)
            parts = _split_args(inner)
            # join parts with SQLite concatenation operator
            joined = " || ".join(parts)
            return f"({joined})"

        transformed = pattern.sub(_repl, query)
        return transformed

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
