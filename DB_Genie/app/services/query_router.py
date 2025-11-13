import logging
from enum import Enum
from typing import Any, Dict

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries the system can handle."""

    VECTOR_SEARCH = "vector_search"
    SQL_QUERY = "sql_query"
    VISUALIZATION = "visualization"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class QueryRouterService:
    """Intelligent query router for determining which service to use."""

    def __init__(self):
        """Initialize query router with keyword patterns."""

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
            "top",
            "bottom",
            "highest",
            "lowest",
            "most",
            "least",
        ]

        # FIX: More aggressive visualization keywords
        self.viz_keywords = [
            "plot",
            "chart",
            "graph",
            "visualize",
            "visualise",
            "draw",
            "show graph",
            "show chart",
            "show plot",
            "display chart",
            "bar chart",
            "line chart",
            "pie chart",
            "create a chart",
            "generate a plot",
            "generate a chart",
        ]

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
        ]

    def route_query(self, query: str, has_database: bool = True) -> Dict[str, Any]:
        """Analyze query and determine routing."""
        query_lower = query.lower()

        # Check for explicit visualization request
        needs_viz = any(keyword in query_lower for keyword in self.viz_keywords)

        # Check for SQL
        is_sql_query = any(keyword in query_lower for keyword in self.sql_keywords)

        # Check for policy
        is_policy_query = any(
            keyword in query_lower for keyword in self.policy_keywords
        )

        # Determine type
        if needs_viz and has_database:
            query_type = QueryType.VISUALIZATION
            confidence = 0.95
            reasoning = "Explicit visualization requested"

        elif is_policy_query and is_sql_query:
            query_type = QueryType.HYBRID
            confidence = 0.7
            reasoning = "Both policy and data query"

        elif is_policy_query:
            query_type = QueryType.VECTOR_SEARCH
            confidence = 0.9
            reasoning = "Policy/document search"

        elif is_sql_query and has_database:
            query_type = QueryType.SQL_QUERY
            confidence = 0.85
            reasoning = "Database query"

        elif has_database:
            query_type = QueryType.SQL_QUERY
            confidence = 0.5
            reasoning = "Default to database"

        else:
            query_type = QueryType.VECTOR_SEARCH
            confidence = 0.8
            reasoning = "Fallback to document search"

        return {
            "query_type": query_type,
            "needs_visualization": needs_viz,
            "confidence": confidence,
            "reasoning": reasoning,
        }
