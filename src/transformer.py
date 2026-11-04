
import logging
import pandas as pd


def transform_data(df):
    logging.info("Starting data transformation")

    # Work on a copy
    df = df.copy()

    # Check required columns
    required_columns = ["age", "salary"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

        # Ensure values are numeric
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        # Check for missing or invalid values
        if df[column].isna().any():
            raise ValueError(
                f"Invalid or missing values found in {column}"
            )

    # Convert age and salary to integers
    df["age"] = df["age"].round().astype(int)
    df["salary"] = df["salary"].round().astype(int)

    # Create salary category
    def salary_category(salary):
        if salary < 30000:
            return "Low"
        elif salary < 40000:
            return "Medium"
        else:
            return "High"

    df["salary_category"] = df["salary"].apply(salary_category)

    logging.info("Data transformation completed successfully")

    return df


if __name__ == "__main__":
    from reader import read_csv
    from cleaner import clean_data

    data = read_csv("data/input/employees.csv")

    cleaned_data = clean_data(data)

    transformed_data = transform_data(cleaned_data)

    print(transformed_data)
