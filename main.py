
from pathlib import Path

from etl.errors import ExtractionError
from etl.extractors import APIExtractor, CSVExtractor
from etl.loader import DataLoader
from etl.pipeline import Pipeline
from etl.transformer import DataTransformer


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

ORDERS_FIELDS = [
    "order_id",
    "order_date",
    "customer_email",
    "city",
    "product_sku",
    "quantity",
    "unit_price_kes",
    "status",
]

USER_FIELDS = ["id", "name", "username", "email"]


def build_pipelines() -> list[Pipeline]:
    """Build pipelines from configuration."""
    orders_pipeline = Pipeline(
        extractor=CSVExtractor(
            str(DATA_DIR / "orders.csv"),
            name="orders",
        ),
        transformer=DataTransformer(
            ORDERS_FIELDS,
            unique_fields=["order_id"],
        ),
        loader=DataLoader(OUTPUT_DIR / "orders_clean.csv"),
        rejected_loader=DataLoader(OUTPUT_DIR / "orders_rejected.csv"),
    )

    users_pipeline = Pipeline(
        extractor=APIExtractor(
            "https://jsonplaceholder.typicode.com/users",
            name="customers",
        ),
        transformer=DataTransformer(USER_FIELDS),
        loader=DataLoader(OUTPUT_DIR / "customers.json"),
    )

    return [orders_pipeline, users_pipeline]


def main() -> None:
    """Run configured pipelines and print a summary."""
    pipelines = build_pipelines()
    summaries = []

    print("=== ETL execution summary ===")

    for pipeline in pipelines:
        summary = pipeline.run()
        summaries.append(summary)
        print(summary.report())
        print()

    succeeded = sum(s.errors == [] for s in summaries)
    failed = len(summaries) - succeeded

    print(
        f"Total pipelines: {len(summaries)} | "
        f"Succeeded: {succeeded} | Failed: {failed}"
    )


if __name__ == "__main__":
    main()
