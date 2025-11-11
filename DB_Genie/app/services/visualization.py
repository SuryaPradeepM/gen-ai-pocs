import base64
import io
from typing import Any, Dict, List, Optional

import matplotlib
import pandas as pd

matplotlib.use("Agg")  # Non-interactive backend
import logging

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

logger = logging.getLogger(__name__)

# Set style for seaborn
sns.set_style("whitegrid")
sns.set_palette("husl")


class VisualizationService:
    """
    Service for generating visualizations from query results.
    Supports both static (matplotlib/seaborn) and interactive (plotly) charts.
    """

    def __init__(self):
        """Initialize visualization service."""
        self.supported_chart_types = [
            "bar",
            "line",
            "pie",
            "scatter",
            "histogram",
            "box",
            "heatmap",
            "area",
            "table",
        ]

    def create_visualization(
        self,
        data: List[Dict[str, Any]],
        chart_type: str = "auto",
        title: Optional[str] = None,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        interactive: bool = True,
    ) -> Dict[str, Any]:
        """
        Create visualization from query results.

        Args:
            data: List of dictionaries containing query results
            chart_type: Type of chart ('auto', 'bar', 'line', 'pie', etc.)
            title: Chart title
            x_column: Column name for x-axis
            y_column: Column name for y-axis
            interactive: If True, use Plotly; if False, use Matplotlib/Seaborn

        Returns:
            Dictionary containing:
                - success: bool
                - image_base64: base64 encoded image (if static)
                - html: HTML string for interactive chart (if interactive)
                - chart_type: detected/used chart type
                - error: error message (if failed)
        """
        try:
            if not data:
                return {"success": False, "error": "No data provided for visualization"}

            # Convert to DataFrame
            df = pd.DataFrame(data)

            # Auto-detect chart type if set to 'auto'
            if chart_type == "auto":
                chart_type = self._detect_chart_type(df)

            # Generate visualization
            if interactive:
                result = self._create_plotly_chart(
                    df, chart_type, title, x_column, y_column
                )
            else:
                result = self._create_static_chart(
                    df, chart_type, title, x_column, y_column
                )

            result["chart_type"] = chart_type
            return result

        except Exception as e:
            logger.error(f"Visualization creation error: {str(e)}")
            return {"success": False, "error": str(e)}

    def _detect_chart_type(self, df: pd.DataFrame) -> str:
        """
        Auto-detect appropriate chart type based on data characteristics.

        Args:
            df: DataFrame containing the data

        Returns:
            Suggested chart type
        """
        n_cols = len(df.columns)
        n_rows = len(df)

        # Check column types
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        # Decision logic
        if n_cols == 2 and len(numeric_cols) == 1 and len(categorical_cols) == 1:
            # One categorical, one numeric -> Bar chart
            return "bar"
        elif n_cols == 2 and len(numeric_cols) == 2:
            # Two numeric -> Scatter plot
            return "scatter"
        elif n_cols >= 3 and len(numeric_cols) >= 2:
            # Multiple numeric columns -> Line chart
            return "line"
        elif len(categorical_cols) == 1 and len(numeric_cols) == 1:
            # Categorical distribution -> Pie chart
            if n_rows <= 10:
                return "pie"
            else:
                return "bar"
        else:
            # Default to table for complex data
            return "table"

    def _create_plotly_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        title: Optional[str],
        x_column: Optional[str],
        y_column: Optional[str],
    ) -> Dict[str, Any]:
        """Create interactive Plotly chart."""
        try:
            # Auto-detect columns if not specified
            if not x_column:
                x_column = df.columns[0]
            if not y_column and len(df.columns) > 1:
                numeric_cols = df.select_dtypes(include=["number"]).columns
                y_column = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[1]

            # Create appropriate chart
            if chart_type == "bar":
                fig = px.bar(
                    df,
                    x=x_column,
                    y=y_column,
                    title=title or f"{y_column} by {x_column}",
                )

            elif chart_type == "line":
                fig = px.line(
                    df,
                    x=x_column,
                    y=y_column,
                    title=title or f"{y_column} over {x_column}",
                )

            elif chart_type == "scatter":
                fig = px.scatter(
                    df,
                    x=x_column,
                    y=y_column,
                    title=title or f"{y_column} vs {x_column}",
                )

            elif chart_type == "pie":
                fig = px.pie(
                    df,
                    names=x_column,
                    values=y_column,
                    title=title or f"Distribution of {y_column}",
                )

            elif chart_type == "histogram":
                fig = px.histogram(
                    df, x=x_column, title=title or f"Distribution of {x_column}"
                )

            elif chart_type == "box":
                fig = px.box(df, y=y_column, title=title or f"Box Plot of {y_column}")

            elif chart_type == "area":
                fig = px.area(
                    df,
                    x=x_column,
                    y=y_column,
                    title=title or f"{y_column} over {x_column}",
                )

            elif chart_type == "table":
                fig = go.Figure(
                    data=[
                        go.Table(
                            header=dict(
                                values=list(df.columns),
                                fill_color="paleturquoise",
                                align="left",
                            ),
                            cells=dict(
                                values=[df[col] for col in df.columns],
                                fill_color="lavender",
                                align="left",
                            ),
                        )
                    ]
                )
                fig.update_layout(title=title or "Data Table")

            else:
                # Default to bar chart
                fig = px.bar(df, x=x_column, y=y_column, title=title or "Chart")

            # Convert to HTML
            html_string = fig.to_html(include_plotlyjs="cdn", full_html=False)

            return {"success": True, "html": html_string, "image_base64": None}

        except Exception as e:
            logger.error(f"Plotly chart creation error: {str(e)}")
            raise

    def _create_static_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        title: Optional[str],
        x_column: Optional[str],
        y_column: Optional[str],
    ) -> Dict[str, Any]:
        """Create static Matplotlib/Seaborn chart."""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            # Auto-detect columns if not specified
            if not x_column:
                x_column = df.columns[0]
            if not y_column and len(df.columns) > 1:
                numeric_cols = df.select_dtypes(include=["number"]).columns
                y_column = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[1]

            # Create appropriate chart
            if chart_type == "bar":
                sns.barplot(data=df, x=x_column, y=y_column, ax=ax)

            elif chart_type == "line":
                sns.lineplot(data=df, x=x_column, y=y_column, ax=ax)

            elif chart_type == "scatter":
                sns.scatterplot(data=df, x=x_column, y=y_column, ax=ax)

            elif chart_type == "histogram":
                sns.histplot(data=df, x=x_column, ax=ax)

            elif chart_type == "box":
                sns.boxplot(data=df, y=y_column, ax=ax)

            else:
                sns.barplot(data=df, x=x_column, y=y_column, ax=ax)

            ax.set_title(title or f"{chart_type.capitalize()} Chart")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
            plt.close(fig)

            return {"success": True, "image_base64": image_base64, "html": None}

        except Exception as e:
            logger.error(f"Static chart creation error: {str(e)}")
            raise
