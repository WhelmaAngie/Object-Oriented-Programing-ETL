
import csv
import json
from pathlib import Path
from typing import Any


class DataLoader:
    """Write records to a CSV or JSON destination."""

    def __init__(self, destination: Path) -> None:
        self.destination = Path(destination)
        self.extension = self.destination.suffix.lower()

        if self.extension not in {".csv", ".json"}:
            raise ValueError(
                f"Unsupported output extension: {self.extension!r}. "
                "Use '.csv' or '.json'."
            )

    def load(self, records: list[dict[str, Any]]) -> int:
        """Write records and return the number written."""
        self.destination.parent.mkdir(parents=True, exist_ok=True)

        if self.extension == ".json":
            with self.destination.open("w", encoding="utf-8") as file:
                json.dump(records, file, indent=2, ensure_ascii=False)
                file.write("\n")

            return len(records)

        # For CSV, use the union of all record keys as column headers.
        fieldnames = []
        seen_fields = set()

        for record in records:
            for field in record:
                if field not in seen_fields:
                    seen_fields.add(field)
                    fieldnames.append(field)

        with self.destination.open(
            "w", newline="", encoding="utf-8-sig"
        ) as file:
            if fieldnames:
                writer = csv.DictWriter(
                    file,
                    fieldnames=fieldnames,
                    extrasaction="ignore",
                )
                writer.writeheader()
                writer.writerows(records)

        return len(records)
