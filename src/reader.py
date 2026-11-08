
import json
import logging
from pathlib import Path

import pandas as pd
import requests


def records_to_dataframe(data, source_name):
    """Convert JSON records into a pandas DataFrame."""

    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            data = data["data"]

        elif isinstance(data.get("results"), list):
            data = data["results"]

        elif isinstance(data.get("users"), list):
            data = data["users"]

        else:
            data = [data]

    if not isinstance(data, list) or not data:
        raise ValueError(f"{source_name} contains no records")

    if not all(isinstance(record, dict) for record in data):
        raise ValueError(
            f"{source_name} must contain a list of JSON objects"
        )

    df = pd.json_normalize(data)

    if df.empty:
        raise ValueError(f"{source_name} contains no records")

    return df


def read_csv(file_path):
    """Read data from a CSV file."""

    file_path = Path(file_path)
    logging.info(f"Reading CSV file: {file_path}")

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")

    if df.empty:
        raise ValueError("CSV file contains no records")

    logging.info(f"CSV loaded successfully: {len(df)} records")

    return df


def read_json(file_path):
    """Read data from a JSON file."""

    file_path = Path(file_path)
    logging.info(f"Reading JSON file: {file_path}")

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON file: {error}")

    df = records_to_dataframe(data, "JSON file")

    logging.info(f"JSON loaded successfully: {len(df)} records")

    return df


def read_api(url, timeout=15):
    """Fetch data from an API and convert it into a DataFrame."""

    logging.info(f"Fetching data from API: {url}")

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.Timeout:
        raise RuntimeError("API request timed out")

    except requests.exceptions.HTTPError as error:
        raise RuntimeError(f"API returned an HTTP error: {error}")

    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Could not connect to API: {error}")

    except ValueError:
        raise ValueError("API did not return valid JSON data")

    # Convert API response into a DataFrame
    df = records_to_dataframe(data, "API response")

    # Create full name from first and last name
    if "firstName" in df.columns and "lastName" in df.columns:
        df["name"] = (
            df["firstName"].fillna("").astype(str).str.strip()
            + " "
            + df["lastName"].fillna("").astype(str).str.strip()
        ).str.strip()

    # Extract city from nested address
    if "address.city" in df.columns:
        df["city"] = df["address.city"]

    elif "address" in df.columns:
        df["city"] = df["address"].apply(
            lambda address: address.get("city")
            if isinstance(address, dict)
            else None
        )

    # Add salary only when the API does not provide it
    if "salary" not in df.columns:
        df["salary"] = 0

    logging.info(
        f"API data loaded successfully: {len(df)} records"
    )

    return df
