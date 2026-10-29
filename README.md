# Object-Oriented ETL Framework

## Project Overview

This project implements a reusable, object-oriented Extract, Transform, Load (ETL) framework for Jumla Logistics. It processes logistics orders from a CSV file and customer records from a REST API.

The framework separates extraction, transformation, loading, and pipeline orchestration into reusable components.

## Features

- Abstract `DataExtractor` base class.
- `CSVExtractor` for reading CSV files.
- `APIExtractor` for retrieving JSON records from a REST API.
- Custom extraction exceptions.
- Required-field and email validation.
- Positive numeric validation for quantity and unit price.
- City-name normalization.
- Configurable duplicate detection.
- Rejected-record tracking with reasons.
- CSV and JSON output support.
- Automatic creation of destination directories.
- Pipeline execution summaries with record counts and status.

## Project Structure

```text
day4-oop-etl/
├── etl/
│   ├── __init__.py
│   ├── errors.py
│   ├── extractors.py
│   ├── transformer.py
│   ├── loader.py
│   └── pipeline.py
├── data/
│   └── orders.csv
├── output/
│   ├── orders_clean.csv
│   ├── orders_rejected.csv
│   └── customers.json
├── main.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements

- Python 3.14 or later
- `requests`

## Installation

Clone the repository and navigate into the project directory:

```bash
git clone <YOUR_REPOSITORY_URL>
cd day4-oop-etl
```

Create and activate a virtual environment with `uv`:

```bash
uv sync
```

Alternatively, create a virtual environment and install dependencies using pip:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Running the ETL Framework

Run both configured pipelines:

```bash
python main.py
```

The orders pipeline reads `data/orders.csv` and produces:

- `output/orders_clean.csv`
- `output/orders_rejected.csv`

The customers pipeline retrieves user records from:

`https://jsonplaceholder.typicode.com/users`

It writes the retrieved records to `output/customers.json`.

The API pipeline requires an internet connection.

## Transformation and Validation

The orders pipeline validates required fields, checks email formats, verifies that quantity and unit price are positive numeric values, normalizes city names, calculates line totals, and rejects duplicate order IDs.

Invalid records are retained in the rejected output with a `reasons` field explaining why they were rejected.

The users pipeline checks the configured required fields: `id`, `name`, `username`, and `email`.

## Error Handling

The framework defines a custom ETL exception hierarchy, including `ETLError`, `ExtractionError`, and `ValidationError`.

Extraction failures, such as a missing CSV file or an unreachable API, are wrapped in `ExtractionError`. The pipeline records extraction errors in its summary rather than allowing an extraction failure to terminate the entire program.

Individual invalid records are rejected while the remaining records continue through the pipeline.

## Output and Reconciliation

Each pipeline reports extracted, valid, rejected, and loaded record counts, along with rejection reasons, duration, and status.

The expected reconciliation rule is:

**Extracted records = Valid records + Rejected records**

A pipeline can have a `PARTIAL` status when it processes records but rejects some of them.

## Verified Run

During development, the orders pipeline processed 25 input rows:

- Valid orders loaded: 19
- Rejected orders: 6
- Rejected records include one duplicate order ID and five other validation failures.

The customers pipeline successfully retrieved and loaded 10 records during the verified run.

These figures describe the development run; results may vary if the input data or API response changes.

## Failure-Handling Checks

The extractors were manually tested with a missing CSV file and an invalid URL. Both failures were caught as `ExtractionError`.

## Technologies

- Python
- Object-oriented programming
- `requests`
- CSV and JSON
- `pathlib`
- `uv`

## Author

Whelma Bange Nyabuto
