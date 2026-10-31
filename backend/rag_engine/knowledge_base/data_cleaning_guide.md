
# Data Cleaning Knowledge Guide

## 1. Missing Values
Missing values occur when a dataset contains empty or unavailable information.

Recommended approaches:
- Use median imputation for numeric columns when data is skewed or contains outliers.
- Use mean imputation for reasonably symmetric numeric data.
- Use mode imputation for categorical columns.
- Consider dropping rows only when appropriate and when information loss is acceptable.
- Always report how many values were changed.

## 2. Duplicate Records
Duplicate records are repeated rows in a dataset.

Recommended approaches:
- Identify exact duplicate rows.
- Check whether duplicates represent genuine repeated events.
- Remove confirmed duplicates only after reviewing their impact.
- Report the number of removed records.

## 3. Outlier Detection
Outliers are unusually high or low values.

Recommended approaches:
- Use the Interquartile Range (IQR) method.
- IQR = Q3 - Q1.
- Lower bound = Q1 - 1.5 * IQR.
- Upper bound = Q3 + 1.5 * IQR.
- Investigate outliers before removing them.
- Do not automatically delete unusual values.

## 4. Incorrect Data Types
A column may contain numbers stored as text.

Recommended approaches:
- Inspect the column values.
- Convert valid numeric text into numeric types.
- Treat whitespace-only strings as missing values.
- Check conversion failures before applying imputation.

## 5. Categorical Data
Categorical columns contain labels or groups.

Recommended approaches:
- Standardize inconsistent labels.
- Remove unnecessary leading and trailing spaces.
- Use the mode for missing categorical values when appropriate.
- Preserve meaningful categories.

## 6. Data Cleaning Safety
- Always preserve the original dataset.
- Perform cleaning on a separate copy.
- Preview proposed changes before applying them.
- Allow users to approve or reject changes.
- Maintain a cleaning history.
- Report all transformations performed.
