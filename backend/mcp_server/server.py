
from pathlib import Path

import pandas as pd
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("LLM Data Cleaning Assistant")

# Locate the uploaded dataset
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "storage" / "uploads" / "telco_customer_churn.csv"


def load_dataset():
    """Load the uploaded CSV dataset."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    return pd.read_csv(DATASET_PATH)


@mcp.tool()
def inspect_dataset() -> str:
    """Show the dataset's dimensions, columns, and data types."""
    df = load_dataset()

    result = [
        f"Total rows: {df.shape[0]}",
        f"Total columns: {df.shape[1]}",
        "",
        "Columns and data types:"
    ]

    for column, dtype in df.dtypes.items():
        result.append(f"{column}: {dtype}")

    return "\n".join(result)


@mcp.tool()
def detect_missing_values() -> str:
    """Find missing and whitespace-only values in each column."""
    df = load_dataset()
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        return "No missing values found."

    return "\n".join(
        f"{column}: {count} missing values"
        for column, count in missing.items()
    )


@mcp.tool()
def detect_duplicates() -> str:
    """Count duplicate rows in the dataset."""
    df = load_dataset()
    count = int(df.duplicated().sum())

    return f"Duplicate rows found: {count}"


@mcp.tool()
def summarize_column(column_name: str) -> str:
    """Summarize a selected dataset column."""
    df = load_dataset()

    if column_name not in df.columns:
        return f"Column '{column_name}' does not exist."

    series = df[column_name]
    numeric = pd.to_numeric(series, errors="coerce")

    if numeric.notna().sum() > 0:
        return (
            f"Column: {column_name}\n"
            f"Data type: {series.dtype}\n"
            f"Non-missing values: {numeric.notna().sum()}\n"
            f"Mean: {numeric.mean():.2f}\n"
            f"Median: {numeric.median():.2f}\n"
            f"Minimum: {numeric.min():.2f}\n"
            f"Maximum: {numeric.max():.2f}"
        )

    return (
        f"Column: {column_name}\n"
        f"Unique values: {series.nunique()}\n"
        f"Most common values:\n{series.value_counts().head(5).to_string()}"
    )


@mcp.tool()
def detect_outliers(column_name: str) -> str:
    """Detect outliers in a numerical column using the IQR method."""

    df = load_dataset()

    if column_name not in df.columns:
        return f"Column '{column_name}' does not exist."

    numeric = pd.to_numeric(
        df[column_name], errors="coerce"
    ).dropna()

    if numeric.empty:
        return f"Column '{column_name}' has no valid numeric values."

    q1 = numeric.quantile(0.25)
    q3 = numeric.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    outliers = numeric[
        (numeric < lower_bound) | (numeric > upper_bound)
    ]

    return (
        f"Column: {column_name}\n"
        f"Q1: {q1:.2f}\n"
        f"Q3: {q3:.2f}\n"
        f"IQR: {iqr:.2f}\n"
        f"Lower Bound: {lower_bound:.2f}\n"
        f"Upper Bound: {upper_bound:.2f}\n"
        f"Outlier Count: {len(outliers)}\n"
        f"Outlier Values (first 10): {outliers.head(10).tolist()}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
