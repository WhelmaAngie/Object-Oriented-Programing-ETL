
import time
from dataclasses import dataclass, field

from etl.errors import ExtractionError
from etl.extractors import DataExtractor
from etl.loader import DataLoader
from etl.transformer import DataTransformer


@dataclass
class RunSummary:
    """Collect statistics and report the result of a pipeline run."""

    source: str
    extracted: int = 0
    valid: int = 0
    rejected: int = 0
    loaded: int = 0
    errors: list[str] = field(default_factory=list)
    rejection_reasons: dict[str, int] = field(default_factory=dict)
    duration: float = 0.0

    @property
    def status(self) -> str:
        if self.errors and self.extracted == 0:
            return "FAILED"
        if self.rejected or self.errors:
            return "PARTIAL"
        return "SUCCESS"

    def report(self) -> str:
        lines = [
            f"Pipeline: {self.source}",
            f"  Extracted : {self.extracted}",
            f"  Valid     : {self.valid}",
            f"  Rejected  : {self.rejected}",
        ]

        for reason, count in sorted(self.rejection_reasons.items()):
            lines.append(f"    - {reason}: {count}")

        lines.extend([
            f"  Loaded    : {self.loaded}",
            f"  Duration  : {self.duration:.2f}s",
            f"  Status    : {self.status}",
        ])

        if self.errors:
            lines.append(f"  Error     : {'; '.join(self.errors)}")

        return "\n".join(lines)


class Pipeline:
    """Run extraction, transformation, and loading for any extractor."""

    def __init__(
        self,
        extractor: DataExtractor,
        transformer: DataTransformer,
        loader: DataLoader,
        rejected_loader: DataLoader | None = None,
    ) -> None:
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader
        self.rejected_loader = rejected_loader

    def run(self) -> RunSummary:
        summary = RunSummary(
            source=(
                f"{self.extractor.name} "
                f"({self.extractor!r} -> {self.loader.destination})"
            )
        )
        start = time.perf_counter()

        try:
            records = self.extractor.extract()
            summary.extracted = len(records)

            valid_records = self.transformer.transform(records)
            rejected_records = self.transformer.rejected_records

            summary.valid = len(valid_records)
            summary.rejected = len(rejected_records)

            for record in rejected_records:
                reason_text = record.get("reasons", "Unknown reason")
                for reason in reason_text.split("; "):
                    summary.rejection_reasons[reason] = (
                        summary.rejection_reasons.get(reason, 0) + 1
                    )

            summary.loaded = self.loader.load(valid_records)

            if self.rejected_loader is not None:
                self.rejected_loader.load(rejected_records)

        except ExtractionError as error:
            summary.errors.append(str(error))

        except OSError as error:
            summary.errors.append(f"Output error: {error}")

        finally:
            summary.duration = time.perf_counter() - start

        return summary
