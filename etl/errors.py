

class ETLError(Exception):
    """Base class for ETL framework errors."""


class ExtractionError(ETLError):
    """Raised when a source cannot be read."""


class ValidationError(ETLError):
    """Raised when a record fails validation."""
