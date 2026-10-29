
import re
from copy import deepcopy
from typing import Any


class DataTransformer:
    """Validate and normalize records while retaining rejected records."""

    def __init__(
        self,
        required_fields: list[str],
        unique_fields: list[str] | None = None,
    ) -> None:
        self.required_fields = required_fields
        self.unique_fields = unique_fields or []
        self.rejected_records: list[dict[str, Any]] = []

    def validate(self, record: dict[str, Any]) -> list[str]:
        """Return reasons why a record is invalid."""
        reasons = []

        for field in self.required_fields:
            value = record.get(field)
            if value is None or str(value).strip() == "":
                reasons.append(f"Missing required field: {field}")

        email = record.get("customer_email", record.get("email"))
        if email is not None and str(email).strip():
            email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
            if not re.match(email_pattern, str(email).strip()):
                reasons.append("Invalid email address")

        for field in ("quantity", "unit_price_kes"):
            if field not in record:
                continue

            value = record[field]
            try:
                if isinstance(value, str):
                    value = value.replace(",", "").strip()

                number = float(value)
                if number <= 0:
                    reasons.append(f"{field} must be greater than zero")
            except (ValueError, TypeError, OverflowError):
                reasons.append(f"{field} must be numeric")

        return reasons

    def clean(self, record: dict[str, Any]) -> dict[str, Any]:
        """Return a normalized copy of a valid record."""
        cleaned = deepcopy(record)

        if isinstance(cleaned.get("city"), str):
            cleaned["city"] = " ".join(
                cleaned["city"].strip().split()
            ).title()

        for field in ("quantity", "unit_price_kes"):
            if field in cleaned:
                value = cleaned[field]

                if isinstance(value, str):
                    value = value.replace(",", "").strip()

                number = float(value)

                if field == "quantity":
                    cleaned[field] = int(number)
                else:
                    cleaned[field] = number

        if "quantity" in cleaned and "unit_price_kes" in cleaned:
            cleaned["line_total_kes"] = round(
                cleaned["quantity"] * cleaned["unit_price_kes"]
            )

        return cleaned

    def transform(
        self, records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Validate, reject invalid or duplicate records, and clean valid ones."""
        self.rejected_records = []
        valid_records = []
        seen_values = {field: set() for field in self.unique_fields}

        for record in records:
            reasons = self.validate(record)

            if not reasons:
                for field in self.unique_fields:
                    value = str(record.get(field, "")).strip()

                    if value and value in seen_values[field]:
                        reasons.append(f"Duplicate {field}: {value}")

            if reasons:
                rejected = deepcopy(record)
                rejected["reasons"] = "; ".join(reasons)
                self.rejected_records.append(rejected)
                continue

            try:
                cleaned = self.clean(record)
                valid_records.append(cleaned)

                for field in self.unique_fields:
                    value = str(record.get(field, "")).strip()
                    if value:
                        seen_values[field].add(value)

            except (ValueError, TypeError, OverflowError) as error:
                rejected = deepcopy(record)
                rejected["reasons"] = f"Cleaning failed: {error}"
                self.rejected_records.append(rejected)

        return valid_records
