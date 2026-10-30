
import os
import pandas as pd


def prepare_cleaning_preview(df):
    cleaned = df.copy()
    actions = []

    # 1. Convert blank strings into missing values
    blank_count = 0

    for column in cleaned.columns:
        blanks = (
            cleaned[column]
            .astype("string")
            .str.strip()
            .eq("")
        )

        count = int(blanks.sum())

        if count > 0:
            cleaned[column] = cleaned[column].replace(
                r"^\s*$", pd.NA, regex=True
            )
            blank_count += count

    if blank_count:
        actions.append(f"Detected {blank_count} blank values.")

    # 2. Convert numeric values stored as text
    for column in cleaned.columns:
        if cleaned[column].dtype == "object":
            converted = pd.to_numeric(
                cleaned[column], errors="coerce"
            )

            original_count = int(cleaned[column].notna().sum())
            converted_count = int(converted.notna().sum())

            if original_count > 0 and original_count == converted_count:
                cleaned[column] = converted
                actions.append(
                    f"Convert '{column}' from text to numeric."
                )

    # 3. Fill missing values
    for column in cleaned.columns:
        missing_count = int(cleaned[column].isna().sum())

        if missing_count == 0:
            continue

        if pd.api.types.is_numeric_dtype(cleaned[column]):
            fill_value = cleaned[column].median()
            cleaned[column] = cleaned[column].fillna(fill_value)

            actions.append(
                f"Fill {missing_count} missing values in "
                f"'{column}' using the median."
            )
        else:
            mode_values = cleaned[column].mode()

            if not mode_values.empty:
                fill_value = mode_values.iloc[0]
                cleaned[column] = cleaned[column].fillna(fill_value)

                actions.append(
                    f"Fill {missing_count} missing values in "
                    f"'{column}' using the most frequent value."
                )

    # 4. Remove duplicate rows
    duplicate_count = int(cleaned.duplicated().sum())

    if duplicate_count > 0:
        cleaned = cleaned.drop_duplicates()
        actions.append(
            f"Remove {duplicate_count} duplicate rows."
        )

    return cleaned, actions


def apply_cleaning(df):
    return prepare_cleaning_preview(df)


if __name__ == "__main__":

    input_path = "storage/uploads/telco_customer_churn.csv"
    output_path = "storage/processed/cleaned_telco_customer_churn.csv"

    original_df = pd.read_csv(input_path)

    cleaned_df, actions = prepare_cleaning_preview(original_df)

    print("\n========== CLEANING PREVIEW ==========")
    print("Original Rows:", len(original_df))
    print("Preview Rows:", len(cleaned_df))

    print("\nProposed Actions:")

    for action in actions:
        print("-", action)

    if not actions:
        print("No cleaning actions required.")

    print("\nOriginal Dataset:", original_df.shape)
    print("Preview Dataset:", cleaned_df.shape)

    # Ask for approval
    approval = input(
        "\nDo you approve these cleaning changes? (y/n): "
    ).strip().lower()

    if approval == "y":

        os.makedirs("storage/processed", exist_ok=True)

        cleaned_df.to_csv(output_path, index=False)

        print("\nCleaning approved!")
        print("Cleaned file exported to:", output_path)
        print("Original file remains unchanged.")

        print("\n========== CLEANING SUMMARY ==========")
        print("Rows Before:", len(original_df))
        print("Rows After:", len(cleaned_df))
        print(
            "Missing Values Before:",
            int(original_df.isna().sum().sum())
            + int(
                original_df.astype(str)
                .apply(lambda col: col.str.strip().eq("").sum())
                .sum()
            )
        )
        print(
            "Missing Values After:",
            int(cleaned_df.isna().sum().sum())
        )

    else:
        print("\nCleaning cancelled. No file was exported.")

    print("\n========== PROCESS COMPLETED ==========")
