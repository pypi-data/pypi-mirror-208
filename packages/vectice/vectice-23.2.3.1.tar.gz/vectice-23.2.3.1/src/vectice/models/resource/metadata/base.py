from __future__ import annotations

from enum import Enum


class DatasetType(Enum):
    """Enumeration that defines in what shape dataset ares."""

    ORIGIN = "ORIGIN"
    """Raw/origin shape."""
    CLEAN = "CLEAN"
    """Clean shape."""
    VALIDATION = "VALIDATION"
    """Validation shape."""
    MODELING = "MODELING"
    """Modeling shape."""


class DatasetSourceUsage(Enum):
    """Enumeration that defines what datasets are used for."""

    TRAINING = "TRAINING"
    """For training datasets."""
    TESTING = "TESTING"
    """For testing datasets."""
    VALIDATION = "VALIDATION"
    """For validation datasets."""


class DatasetSourceOrigin(Enum):
    """Enumeration that defines where datasets comes from."""

    S3 = "S3"
    """S3 storage."""
    REDSHIFT = "REDSHIFT"
    """Redshift storage."""
    GCS = "GCS"
    """Google Cloud Storage."""
    BIGQUERY = "BIGQUERY"
    """BigQuery storage."""
    SNOWFLAKE = "SNOWFLAKE"
    """Snowflake storage."""
    LOCAL = "LOCAL"
    """Local storage."""
    OTHER = "OTHER"
    """Other storage."""


class DatasetSourceType(Enum):
    """Enumeration that defines the type of datasets."""

    DB = "DB"
    """DB source."""
    FILES = "FILES"
    """Files source."""


class Metadata:
    """This class describes the metadata of a dataset."""

    def __init__(
        self,
        type: DatasetSourceType,
        size: int | None = None,
        usage: DatasetSourceUsage | None = None,
        origin: str | None = None,
    ):
        """Initialize a metadata instance.

        Parameters:
            size: The size of the file.
            type: The type of file.
            usage: The usage made of the data.
            origin: The origin of the data.
        """
        self.size = size
        self.type = type
        self.origin = origin
        self.usage = usage

    def asdict(self) -> dict:
        return {
            "size": self.size,
            "type": self.type.value,
            "usage": self.usage.value if self.usage else None,
            "origin": self.origin,
        }
