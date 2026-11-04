
import pandas as pd
import logging


def clean_data(df, missing_name_value="Unknown"):
    logging.info("Starting data cleaning")

    # Work on a copy to protect the original data
    df = df.copy()

    # Check whether input is empty
    if df.empty:
        raise ValueError("Input data contains no records")

    # Remove spaces from column names
    df.columns = df.columns.str.strip()

    # Check required columns
    required_columns = [
        "id",
        "name",
        "age",
        "salary",
        "city"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        logging.error(f"Missing required columns: {missing_columns}")
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Remove extra spaces from text columns
    text_columns = df.select_dtypes(include="object").columns

    for column in text_columns:
        df[column] = df[column].str.strip()

    # Replace empty strings with missing values
    df.replace("", pd.NA, inplace=True)

    # Fill missing names
    df["name"] = df["name"].fillna(missing_name_value)

    # Convert age and salary into numeric values
    for column in ["age", "salary"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        # Check whether all values are missing or invalid
        if df[column].isna().all():
            raise ValueError(
                f"Cannot clean {column}: all values are missing or invalid"
            )

        # Fill missing values using median
        median_value = df[column].median()
        missing_count = df[column].isna().sum()

        df[column] = df[column].fillna(median_value)

        if missing_count > 0:
            logging.info(
                f"Filled {missing_count} missing values in {column}"
            )

    # Remove duplicate records
    original_count = len(df)
    df.drop_duplicates(inplace=True)
    removed_count = original_count - len(df)

    if removed_count > 0:
        logging.info(f"Removed {removed_count} duplicate records")

    logging.info("Data cleaning completed")

    return df
