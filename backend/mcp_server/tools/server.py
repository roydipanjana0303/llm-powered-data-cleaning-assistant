
from mcp.server import MCPServer
import pandas as pd

mcp = MCPServer("LLM Data Cleaning Assistant")

DATASET_PATH = "storage/uploads/telco_customer_churn.csv"


@mcp.tool()
def inspect_dataset() -> dict:
    """Inspect the uploaded dataset."""

    df = pd.read_csv(DATASET_PATH)

    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "duplicate_rows": int(df.duplicated().sum())
    }


@mcp.tool()
def detect_missing_values() -> dict:
    """Detect missing and blank values."""

    df = pd.read_csv(DATASET_PATH)
    report = {}

    for column in df.columns:
        missing = int(
            df[column].isna().sum()
            + df[column].astype(str).str.strip().eq("").sum()
        )

        if missing > 0:
            report[column] = missing

    return report


@mcp.tool()
def detect_duplicates() -> dict:
    """Detect duplicate rows."""

    df = pd.read_csv(DATASET_PATH)

    return {
        "duplicate_rows": int(df.duplicated().sum())
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
