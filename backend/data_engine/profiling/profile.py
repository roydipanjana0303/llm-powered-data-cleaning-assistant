
import pandas as pd


def load_dataset(file_path):
    """
    Load a CSV dataset using Pandas.
    """
    df = pd.read_csv(file_path)
    return df


def profile_dataset(df):
    """
    Analyze the basic data quality of a dataset.
    """

    profile = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": []
    }

    for column in df.columns:

        # Count normal missing values (NaN)
        normal_missing = df[column].isnull().sum()

        # Count hidden missing values (empty strings or spaces)
        hidden_missing = (
            df[column]
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

        # Calculate total missing values
        missing_count = int(normal_missing + hidden_missing)

        # Calculate missing percentage
        missing_percentage = round(
            (missing_count / len(df)) * 100, 2
        )

        # Count unique values
        unique_count = int(df[column].nunique())

        # Store column information
        column_info = {
            "column_name": column,
            "data_type": str(df[column].dtype),
            "missing_values": missing_count,
            "missing_percentage": missing_percentage,
            "unique_values": unique_count
        }

        profile["columns"].append(column_info)

    return profile


if __name__ == "__main__":

    # Dataset location
    file_path = "storage/uploads/telco_customer_churn.csv"

    # Load dataset
    df = load_dataset(file_path)

    # Generate profile
    result = profile_dataset(df)

    # Display dataset summary
    print("\n========== DATASET PROFILE ==========")

    print("Total Rows:", result["total_rows"])
    print("Total Columns:", result["total_columns"])
    print("Duplicate Rows:", result["duplicate_rows"])

    # Display column analysis
    print("\n========== COLUMN ANALYSIS ==========")

    for column in result["columns"]:

        print("\nColumn:", column["column_name"])
        print("Data Type:", column["data_type"])
        print("Missing Values:", column["missing_values"])
        print("Missing Percentage:", column["missing_percentage"], "%")
        print("Unique Values:", column["unique_values"])

    print("\n========== PROFILING COMPLETED ==========")
