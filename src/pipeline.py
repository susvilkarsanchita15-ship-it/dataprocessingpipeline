import json
import logging
from pathlib import Path

from reader import read_csv, read_json, read_api
from cleaner import clean_data
from transformer import transform_data


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config(config_path):
    config_path = Path(config_path)

    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    required_keys = [
        "output_file",
        "log_file",
        "missing_name_value",
        "input_format",
        "output_format"
    ]

    for key in required_keys:
        if key not in config:
            raise ValueError(
                f"Missing configuration setting: {key}"
            )

    return config


def setup_logging(log_file):
    log_path = PROJECT_ROOT / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True
    )


def run_pipeline(config_path):

    try:
        config = load_config(config_path)

        setup_logging(config["log_file"])

        logging.info("Pipeline started")

        input_format = config["input_format"].lower()
        output_format = config["output_format"].lower()

        if input_format not in ["csv", "json", "api"]:
            raise ValueError(
                f"Unsupported input format: {input_format}"
            )

        if output_format not in ["csv", "json"]:
            raise ValueError(
                f"Unsupported output format: {output_format}"
            )

        # Read input data
        if input_format == "csv":
            df = read_csv(
                PROJECT_ROOT / config["input_file"]
            )

        elif input_format == "json":
            df = read_json(
                PROJECT_ROOT / config["input_file"]
            )

        else:
            if not config.get("api_url"):
                raise ValueError(
                    "API URL is missing from configuration"
                )

            df = read_api(config["api_url"])

        input_rows = len(df)

        logging.info(f"Input records: {input_rows}")

        # Clean data
        df = clean_data(
            df,
            config["missing_name_value"]
        )

        # Transform data
        df = transform_data(df)

        # Save output
        output_path = PROJECT_ROOT / config["output_file"]
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if output_format == "csv":
            df.to_csv(output_path, index=False)
        else:
            df.to_json(
                output_path,
                orient="records",
                indent=4
            )

        logging.info("Pipeline completed successfully")

        print("Pipeline completed successfully!")
        print(f"Input records: {input_rows}")
        print(f"Output records: {len(df)}")
        print(f"Output file: {output_path}")

    except Exception as error:
        logging.exception("Pipeline failed")
        print(f"Pipeline failed: {error}")
        raise