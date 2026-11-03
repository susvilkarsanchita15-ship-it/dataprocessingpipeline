# Data Processing Pipeline

A Python-based data processing pipeline that reads raw data from CSV and JSON files, cleans and transforms the data, handles missing values and invalid data, and generates structured output files.

## Features

- Read data from CSV and JSON files
- Handle missing values
- Handle invalid data and type conversion
- Remove unnecessary spaces
- Validate required columns
- Remove duplicate records
- Create salary categories
- Export processed data as CSV or JSON
- Logging for pipeline activities and errors
- Configuration using a JSON configuration file

## Project Structure

```text
DATA-PROCESSING-PIPELINE/
│
├── data/
│   ├── input/
│   │   ├── employees.csv
│   │   └── employees.json
│   │
│   └── output/
│
├── src/
│   ├── __init__.py
│   ├── reader.py
│   ├── cleaner.py
│   ├── transformer.py
│   ├── pipeline.py
│   └── main.py
│
├── config/
│   └── config.json
│
├── logs/
│
├── requirements.txt
├── .gitignore
└── README.md