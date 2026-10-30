
import pandas as pd
import numpy as np


def load_dataset(file_path):
    return pd.read_csv(file_path)


def profile_dataset(df):

    profile = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": [],
        "quality_issues": []
    }

    for column in df.columns:

        series = df[column]

        # Detect missing and blank values
        missing = int(
            series.isnull().sum()
            + series.astype(str).str.strip().eq("").sum()
        )

        # Check whether text columns contain numeric values
        converted = pd.to_numeric(series, errors="coerce")
        valid_numeric = series.notna() & series.astype(str).str.strip().ne("")
        numeric_count = int(converted[valid_numeric].notna().sum())

        is_numeric = pd.api.types.is_numeric_dtype(series)

        if not is_numeric and numeric_count > 0:
            if numeric_count == int(valid_numeric.sum()):
                data_type_status = "Numeric values stored as text"
                profile["quality_issues"].append(
                    f"{column}: Numeric values are stored as text."
                )
            else:
                data_type_status = "Text or mixed values"
        else:
            data_type_status = "Correct or non-numeric type"

        info = {
            "column_name": column,
            "data_type": str(series.dtype),
            "data_type_status": data_type_status,
            "missing_values": missing,
            "missing_percentage": round(
                missing / len(df) * 100, 2
            ),
            "unique_values": int(series.nunique())
        }

        # Numeric statistics
        numeric_series = (
            converted.dropna()
            if not is_numeric
            else series.dropna()
        )

        if is_numeric or (
            numeric_count == int(valid_numeric.sum())
            and numeric_count > 0
        ):

            numeric_series = pd.to_numeric(
                series, errors="coerce"
            ).dropna()

            info["statistics"] = {
                "mean": round(float(numeric_series.mean()), 2),
                "median": round(float(numeric_series.median()), 2),
                "minimum": float(numeric_series.min()),
                "maximum": float(numeric_series.max()),
                "standard_deviation": round(
                    float(numeric_series.std()), 2
                )
            }

            # Outlier detection using IQR
            q1 = numeric_series.quantile(0.25)
            q3 = numeric_series.quantile(0.75)
            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            outliers = int(
                ((numeric_series < lower) |
                 (numeric_series > upper)).sum()
            )

            info["outliers"] = outliers

        else:
            # Categorical value frequency
            info["top_values"] = (
                series.value_counts()
                .head(5)
                .to_dict()
            )

        profile["columns"].append(info)

    if profile["duplicate_rows"] > 0:
        profile["quality_issues"].append(
            f"Dataset contains {profile['duplicate_rows']} duplicate rows."
        )

    return profile


if __name__ == "__main__":

    file_path = "storage/uploads/telco_customer_churn.csv"

    df = load_dataset(file_path)
    result = profile_dataset(df)

    print("\n========== DATASET PROFILE ==========")
    print("Rows:", result["total_rows"])
    print("Columns:", result["total_columns"])
    print("Duplicate Rows:", result["duplicate_rows"])

    print("\n========== COLUMN ANALYSIS ==========")

    for column in result["columns"]:

        print("\nColumn:", column["column_name"])
        print("Data Type:", column["data_type"])
        print("Type Status:", column["data_type_status"])
        print("Missing Values:", column["missing_values"])
        print("Missing Percentage:", column["missing_percentage"], "%")
        print("Unique Values:", column["unique_values"])

        if "statistics" in column:
            print("Statistics:", column["statistics"])
            print("Outliers:", column["outliers"])

        if "top_values" in column:
            print("Top Values:", column["top_values"])

    print("\n========== QUALITY ISSUES ==========")

    for issue in result["quality_issues"]:
        print("-", issue)

    print("\n========== PROFILING COMPLETED ==========")
