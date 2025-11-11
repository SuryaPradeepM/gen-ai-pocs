import logging
import re
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries the system can handle."""

    VECTOR_SEARCH = "vector_search"  # PDF/document search
    SQL_QUERY = "sql_query"  # Database query
    VISUALIZATION = "visualization"  # Needs chart/graph
    HYBRID = "hybrid"  # Both vector search and SQL
    UNKNOWN = "unknown"


class QueryRouterService:
    """
    Intelligent query router that determines which service(s) to use
    based on the user's question.
    """

    def __init__(self):
        """Initialize query router with keyword patterns."""

        # Keywords that indicate SQL/database queries
        self.sql_keywords = [
            "how many",
            "count",
            "total",
            "average",
            "sum",
            "maximum",
            "minimum",
            "list all",
            "show all",
            "find all",
            "get all",
            "employees",
            "leaves",
            "departments",
            "records",
            "calculate",
            "statistics",
            "report",
            "aggregate",
        ]

        # Keywords that indicate visualization needs
        self.viz_keywords = [
            "show graph",
            "show chart",
            "plot",
            "visualize",
            "graph",
            "chart",
            "draw",
            "display chart",
            "trends",
            "comparison",
            "distribution",
            "breakdown",
            "show me a",
        ]

        # Keywords that indicate policy/document search
        self.policy_keywords = [
            "policy",
            "policies",
            "document",
            "guideline",
            "procedure",
            "rule",
            "regulation",
            "handbook",
            "manual",
            "what is the policy",
            "according to",
            "policy states",
            "policy says",
        ]

    def route_query(self, query: str, has_database: bool = True) -> Dict[str, Any]:
        """
        Analyze query and determine which service(s) to use.

        Args:
            query: User's natural language query
            has_database: Whether database is available and initialized

        Returns:
            Dictionary containing:
                - query_type: QueryType enum
                - needs_visualization: bool
                - confidence: float (0-1)
                - reasoning: str explaining the routing decision
        """
        query_lower = query.lower()

        # Check for visualization keywords
        needs_viz = any(keyword in query_lower for keyword in self.viz_keywords)

        # Check for SQL keywords
        is_sql_query = any(keyword in query_lower for keyword in self.sql_keywords)

        # Check for policy keywords
        is_policy_query = any(
            keyword in query_lower for keyword in self.policy_keywords
        )

        # Determine query type
        if is_policy_query and is_sql_query:
            query_type = QueryType.HYBRID
            confidence = 0.7
            reasoning = "Query mentions both policies and structured data"

        elif is_policy_query and not has_database:
            query_type = QueryType.VECTOR_SEARCH
            confidence = 0.9
            reasoning = "Query about policies/documents"

        elif is_sql_query and has_database:
            query_type = QueryType.SQL_QUERY
            confidence = 0.85
            reasoning = "Query requires structured data from database"

        elif needs_viz:
            if has_database:
                query_type = QueryType.VISUALIZATION
                confidence = 0.9
                reasoning = "Query explicitly requests visualization"
            else:
                query_type = QueryType.VECTOR_SEARCH
                confidence = 0.6
                reasoning = "Visualization requested but no database available"

        elif has_database:
            # Default to SQL if database is available
            query_type = QueryType.SQL_QUERY
            confidence = 0.5
            reasoning = "General query routed to database"

        else:
            # Default to vector search
            query_type = QueryType.VECTOR_SEARCH
            confidence = 0.8
            reasoning = "No database available, using document search"

        return {
            "query_type": query_type,
            "needs_visualization": needs_viz,
            "confidence": confidence,
            "reasoning": reasoning,
        }

    def should_use_sql(self, query: str) -> bool:
        """Quick check if query should use SQL."""
        return any(keyword in query.lower() for keyword in self.sql_keywords)

    def should_visualize(self, query: str) -> bool:
        """Quick check if query needs visualization."""
        return any(keyword in query.lower() for keyword in self.viz_keywords)
