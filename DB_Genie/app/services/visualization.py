import base64
import io
import json
from typing import Any, Dict, List, Optional

import matplotlib
import pandas as pd

matplotlib.use("Agg")  # Non-GUI backend
import logging

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

# Clean styling
plt.style.use("seaborn-v0_8-darkgrid")


class VisualizationService:
    """
    LLM-guided visualization service that generates intelligent matplotlib charts.
    """

    def __init__(self):
        """Initialize visualization service."""
        logger.info("VisualizationService initialized with LLM guidance")

    def create_visualization(
        self,
        data: List[Dict[str, Any]],
        chart_type: str = "auto",
        title: Optional[str] = None,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        interactive: bool = False,  # Ignored
        user_query: Optional[str] = None,  # NEW: For LLM context
    ) -> Dict[str, Any]:
        """
        Create an intelligent matplotlib chart using LLM guidance.

        Args:
            data: List of dictionaries containing query results
            chart_type: 'auto' uses LLM to decide, or specify explicitly
            title: Chart title (LLM generates if None)
            x_column: X-axis column (LLM selects if None)
            y_column: Y-axis column (LLM selects if None)
            interactive: Ignored (always static images)
            user_query: Original user query for context

        Returns:
            Dictionary with success status and base64-encoded image
        """
        try:
            if not data:
                return {
                    "success": False,
                    "error": "No data provided",
                    "image_base64": None,
                    "chart_type": None,
                }

            # Convert to DataFrame
            df = pd.DataFrame(data)

            # Use LLM to determine chart parameters if needed
            if chart_type == "auto" or not x_column or not y_column:
                chart_params = self._llm_guided_chart_params(df, user_query)

                if not chart_params.get("success"):
                    # Fallback to heuristics
                    logger.warning("LLM guidance failed, using fallback heuristics")
                    chart_params = self._fallback_chart_params(df, user_query)

                chart_type = chart_params.get("chart_type", chart_type)
                x_column = chart_params.get("x_column", x_column)
                y_column = chart_params.get("y_column", y_column)
                title = chart_params.get("title", title)

            # Validate columns exist
            if x_column not in df.columns:
                logger.error(
                    f"X column '{x_column}' not in data. Available: {df.columns.tolist()}"
                )
                x_column = df.columns[0]

            if y_column not in df.columns:
                logger.error(
                    f"Y column '{y_column}' not in data. Available: {df.columns.tolist()}"
                )
                numeric_cols = df.select_dtypes(include=["number"]).columns
                y_column = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[-1]

            # Generate the chart
            image_base64 = self._generate_chart(
                df=df,
                chart_type=chart_type,
                x_column=x_column,
                y_column=y_column,
                title=title,
            )

            logger.info(
                f"Successfully created {chart_type} chart: {x_column} vs {y_column}"
            )

            return {
                "success": True,
                "image_base64": image_base64,
                "chart_type": chart_type,
                "x_column": x_column,
                "y_column": y_column,
                "title": title,
                "html": None,
                "error": None,
            }

        except Exception as e:
            logger.error(f"Visualization error: {str(e)}")
            plt.close("all")
            return {
                "success": False,
                "error": str(e),
                "image_base64": None,
                "chart_type": None,
                "html": None,
            }

    def _llm_guided_chart_params(
        self, df: pd.DataFrame, user_query: Optional[str]
    ) -> Dict[str, Any]:
        """
        Use LLM to intelligently determine chart parameters.

        Args:
            df: DataFrame with the data
            user_query: Original user query

        Returns:
            Dictionary with chart_type, x_column, y_column, title
        """
        try:
            from app.services.azure_openai import AzureOpenAIService

            openai_service = AzureOpenAIService()

            # Prepare data summary for LLM
            columns_info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                sample_values = df[col].head(3).tolist()
                columns_info.append(
                    {
                        "column_name": col,
                        "data_type": dtype,
                        "sample_values": sample_values,
                    }
                )

            # Create LLM prompt
            prompt = f"""You are a data visualization expert. Analyze the following data and user query to determine the best chart parameters.

USER QUERY: {user_query or "Show the data"}

DATA COLUMNS:
{json.dumps(columns_info, indent=2)}

DATA SAMPLE (first 3 rows):
{df.head(3).to_dict("records")}

TASK: Return a JSON object with the following fields:
{{
  "chart_type": "bar" | "line" | "pie" | "scatter",
  "x_column": "column_name_for_x_axis",
  "y_column": "column_name_for_y_axis",
  "title": "Descriptive chart title",
  "reasoning": "Brief explanation of choices"
}}

RULES:
1. Choose the most appropriate chart type for the data and query
2. For categorical vs numeric data, use bar charts
3. For time series or trends, use line charts
4. For distributions/proportions, use pie charts (only if ≤10 categories)
5. Select columns that best answer the user's question
6. Column names MUST exactly match the available columns
7. Title should be clear and descriptive (not too long)

Return ONLY the JSON object, no other text."""

            messages = [
                {
                    "role": "system",
                    "content": "You are a data visualization expert. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ]

            # Get LLM response
            response = openai_service.get_completion(
                messages, temperature=0.0, max_completion_tokens=500
            )

            # Parse JSON response
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()

            chart_params = json.loads(response)

            # Validate required fields
            required_fields = ["chart_type", "x_column", "y_column", "title"]
            if all(field in chart_params for field in required_fields):
                logger.info(
                    f"LLM chart guidance: {chart_params.get('reasoning', 'No reasoning')}"
                )
                chart_params["success"] = True
                return chart_params
            else:
                logger.error(f"LLM response missing required fields: {chart_params}")
                return {"success": False}

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse LLM JSON response: {str(e)}\nResponse: {response}"
            )
            return {"success": False}
        except Exception as e:
            logger.error(f"LLM guidance error: {str(e)}")
            return {"success": False}

    def _fallback_chart_params(
        self, df: pd.DataFrame, user_query: Optional[str]
    ) -> Dict[str, Any]:
        """
        Fallback heuristics if LLM guidance fails.

        Args:
            df: DataFrame with the data
            user_query: Original user query

        Returns:
            Dictionary with chart_type, x_column, y_column, title
        """
        query_lower = (user_query or "").lower()

        # Get column types
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        # Select x_column (prefer name/title columns)
        x_column = None
        name_keywords = ["name", "title", "department", "category", "type", "employee"]
        for col in categorical_cols:
            if any(keyword in col.lower() for keyword in name_keywords):
                x_column = col
                break
        if not x_column and categorical_cols:
            x_column = categorical_cols[0]
        if not x_column:
            x_column = df.columns[0]

        # Select y_column (prefer value columns based on query)
        y_column = None
        value_keywords = {
            "salary": ["salary", "pay", "wage", "compensation"],
            "count": ["count", "total", "number", "quantity"],
            "days": ["days", "hours", "time", "duration"],
            "rating": ["rating", "score", "review"],
        }

        for term, keywords in value_keywords.items():
            if term in query_lower:
                for col in numeric_cols:
                    if any(kw in col.lower() for kw in keywords):
                        y_column = col
                        break
                if y_column:
                    break

        if not y_column and numeric_cols:
            y_column = numeric_cols[0]
        if not y_column:
            y_column = df.columns[-1]

        # Determine chart type
        n_rows = len(df)
        if n_rows <= 10:
            chart_type = "bar"
        elif "trend" in query_lower or "over time" in query_lower:
            chart_type = "line"
        elif "distribution" in query_lower and n_rows <= 10:
            chart_type = "pie"
        else:
            chart_type = "bar"

        # Generate title
        title = f"{y_column.replace('_', ' ').title()} by {x_column.replace('_', ' ').title()}"

        return {
            "chart_type": chart_type,
            "x_column": x_column,
            "y_column": y_column,
            "title": title,
            "success": True,
        }

    def _generate_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        x_column: str,
        y_column: str,
        title: str,
    ) -> str:
        """
        Generate the actual matplotlib chart and return as base64.

        Args:
            df: DataFrame with data
            chart_type: Type of chart
            x_column: Column for x-axis
            y_column: Column for y-axis
            title: Chart title

        Returns:
            Base64-encoded PNG image
        """
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 7))

        # Sort data by y_column for better visualization
        df_sorted = df.sort_values(by=y_column, ascending=False).head(20)  # Top 20 max

        if chart_type == "bar":
            bars = ax.bar(
                df_sorted[x_column],
                df_sorted[y_column],
                color="steelblue",
                alpha=0.8,
                edgecolor="navy",
            )

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                label = f"{height:,.0f}" if height > 100 else f"{height:.1f}"
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    label,
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    fontweight="bold",
                )

            ax.set_ylabel(
                y_column.replace("_", " ").title(), fontsize=12, fontweight="bold"
            )
            ax.set_xlabel(
                x_column.replace("_", " ").title(), fontsize=12, fontweight="bold"
            )
            ax.tick_params(axis="x", rotation=45)

        elif chart_type == "line":
            ax.plot(
                df_sorted[x_column],
                df_sorted[y_column],
                marker="o",
                linewidth=2.5,
                markersize=8,
                color="steelblue",
            )
            ax.set_ylabel(
                y_column.replace("_", " ").title(), fontsize=12, fontweight="bold"
            )
            ax.set_xlabel(
                x_column.replace("_", " ").title(), fontsize=12, fontweight="bold"
            )
            ax.grid(True, alpha=0.3, linestyle="--")
            ax.tick_params(axis="x", rotation=45)

        elif chart_type == "pie":
            # Limit to top 10 for pie charts
            df_pie = df_sorted.head(10)
            colors = plt.cm.Set3(range(len(df_pie)))
            wedges, texts, autotexts = ax.pie(
                df_pie[y_column],
                labels=df_pie[x_column],
                autopct="%1.1f%%",
                startangle=90,
                colors=colors,
                textprops={"fontsize": 10},
            )
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")
            ax.axis("equal")

        elif chart_type == "scatter":
            ax.scatter(
                df_sorted[x_column],
                df_sorted[y_column],
                s=100,
                alpha=0.6,
                color="steelblue",
                edgecolors="navy",
            )
            ax.set_ylabel(
                y_column.replace("_", " ").title(), fontsize=12, fontweight="bold"
            )
            ax.set_xlabel(
                x_column.replace("_", " ").title(), fontsize=12, fontweight="bold"
            )
            ax.grid(True, alpha=0.3)

        else:
            # Default to bar
            ax.bar(
                df_sorted[x_column], df_sorted[y_column], color="steelblue", alpha=0.8
            )

        # Set title
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

        # Rotate x-axis labels for readability
        if chart_type != "pie":
            plt.xticks(rotation=45, ha="right")

        plt.tight_layout()

        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(
            buffer, format="png", dpi=150, bbox_inches="tight", facecolor="white"
        )
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close(fig)

        return image_base64
