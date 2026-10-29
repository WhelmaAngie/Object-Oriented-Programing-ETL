
import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import requests

from etl.errors import ExtractionError
from abc import ABC, abstractmethod
from typing import Any


class DataExtractor(ABC):
    """Common interface for every data source."""

    def __init__(self, source: str, name: str | None = None) -> None:
        # Store configuration without reading the source
        self.source = source
        self.name = name or source

    @abstractmethod
    def extract(self) -> list[dict[str, Any]]:
        """Return the raw records from the source."""
        pass

    def __repr__(self) -> str:
        """Return a readable description of this extractor."""
        return (
            f"{self.__class__.__name__}"
            f"(name={self.name!r}, source={self.source!r})"
        )


class CSVExtractor(DataExtractor):
    """Reads records from a CSV file."""

    def extract(self) -> list[dict[str, Any]]:
        try:
            with Path(self.source).open(
                "r", newline="", encoding="utf-8-sig"
            ) as file:
                return list(csv.DictReader(file))

        except (OSError, csv.Error) as error:
            raise ExtractionError(
                f"Could not read CSV source '{self.source}': {error}"
            ) from error


class APIExtractor(DataExtractor):
    """Reads records from a JSON HTTP endpoint."""

    def __init__(
        self,
        source: str,
        name: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        super().__init__(source, name)
        self.timeout = timeout

    def __repr__(self) -> str:
        """Include the request timeout in the extractor description."""
        return (
            f"{self.__class__.__name__}"
            f"(name={self.name!r}, source={self.source!r}, "
            f"timeout={self.timeout!r})"
        )

    def extract(self) -> list[dict[str, Any]]:
        try:
            response = requests.get(self.source, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list) or not all(
                isinstance(record, dict) for record in data
            ):
                raise ExtractionError(
                    f"API source '{self.source}' must return a JSON list of objects"
                )

            return data

        except requests.RequestException as error:
            raise ExtractionError(
                f"Could not fetch API source '{self.source}': {error}"
            ) from error
        except ValueError as error:
            raise ExtractionError(
                f"API source '{self.source}' returned invalid JSON"
            ) from error
