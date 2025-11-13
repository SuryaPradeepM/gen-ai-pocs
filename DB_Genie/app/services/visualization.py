import base64
import io
from typing import Any, Dict, List, Optional

import matplotlib
import pandas as pd

matplotlib.use("Agg")  # CRITICAL: Non-GUI backend
import logging

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

# Simple, clean styling
plt.style.use("seaborn-v0_8-darkgrid")


class VisualizationService:
    """
    Simplified visualization service that generates matplotlib charts as base64 images.
    """

    def __init__(self):
        """Initialize visualization service."""
        logger.info("VisualizationService initialized")

    def create_visualization(
        self,
        data: List[Dict[str, Any]],
        chart_type: str = "auto",
        title: Optional[str] = None,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        interactive: bool = False,  # Ignored - always static
    ) -> Dict[str, Any]:
        """
        Create a static matplotlib chart from data and return as base64 image.

        Args:
            data: List of dictionaries containing query results
            chart_type: Type of chart ('auto', 'bar', 'line', 'pie')
            title: Chart title
            x_column: Column for x-axis
            y_column: Column for y-axis
            interactive: Ignored (always generates static images)

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

            # Auto-detect chart type
            if chart_type == "auto":
                chart_type = self._detect_chart_type(df)

            # Auto-detect columns if not specified
            if not x_column:
                # Find first categorical or string column
                for col in df.columns:
                    if (
                        df[col].dtype == "object"
                        or col.endswith("_name")
                        or col.endswith("_id")
                    ):
                        x_column = col
                        break
                if not x_column:
                    x_column = df.columns[0]

            if not y_column:
                # Find first numeric column
                numeric_cols = df.select_dtypes(include=["number"]).columns
                y_column = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[-1]

            # Create the chart
            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == "bar":
                bars = ax.bar(df[x_column], df[y_column], color="steelblue", alpha=0.8)
                ax.set_ylabel(y_column.replace("_", " ").title())
                ax.set_xlabel(x_column.replace("_", " ").title())

                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.0,
                        height,
                        f"{height:,.0f}" if height > 100 else f"{height:.1f}",
                        ha="center",
                        va="bottom",
                        fontsize=9,
                    )

            elif chart_type == "line":
                ax.plot(
                    df[x_column], df[y_column], marker="o", linewidth=2, markersize=6
                )
                ax.set_ylabel(y_column.replace("_", " ").title())
                ax.set_xlabel(x_column.replace("_", " ").title())
                ax.grid(True, alpha=0.3)

            elif chart_type == "pie":
                ax.pie(
                    df[y_column], labels=df[x_column], autopct="%1.1f%%", startangle=90
                )
                ax.axis("equal")

            else:
                # Default to bar
                ax.bar(df[x_column], df[y_column], color="steelblue", alpha=0.8)

            # Set title
            if title:
                ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
            else:
                ax.set_title(
                    f"{y_column.replace('_', ' ').title()} by {x_column.replace('_', ' ').title()}",
                    fontsize=14,
                    fontweight="bold",
                    pad=20,
                )

            # Rotate x-axis labels if they're long
            if chart_type != "pie":
                plt.xticks(rotation=45, ha="right")

            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
            plt.close(fig)

            logger.info(f"Successfully created {chart_type} chart")

            return {
                "success": True,
                "image_base64": image_base64,
                "chart_type": chart_type,
                "html": None,
                "error": None,
            }

        except Exception as e:
            logger.error(f"Visualization error: {str(e)}")
            plt.close("all")  # Cleanup
            return {
                "success": False,
                "error": str(e),
                "image_base64": None,
                "chart_type": None,
                "html": None,
            }

    def _detect_chart_type(self, df: pd.DataFrame) -> str:
        """Auto-detect appropriate chart type based on data."""
        n_rows = len(df)
        numeric_cols = df.select_dtypes(include=["number"]).columns

        # Simple heuristic
        if n_rows <= 10 and len(numeric_cols) >= 1:
            return "bar"
        elif n_rows > 10 and len(numeric_cols) >= 1:
            return "line"
        else:
            return "bar"
