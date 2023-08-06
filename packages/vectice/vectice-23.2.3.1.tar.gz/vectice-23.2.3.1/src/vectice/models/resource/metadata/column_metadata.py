from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class ColumnCategoryType(Enum):
    """Enumeration of the column category types."""

    BOOLEAN = "BOOLEAN"
    NUMERICAL = "NUMERICAL"
    DATE = "DATE"
    TEXT = "TEXT"
    CATEGORICAL = "CATEGORICAL"


@dataclass
class StatValue:
    """Model a key-value pair of a column statistic.

    Parameters:
        key: The key to identify the statistic.
        value: The value of the statistic.
    """

    key: str
    value: int | float | str

    def __post_init__(self):
        if isinstance(self.value, np.generic):
            self.value = self.value.item()
        if not isinstance(self.value, (int, float, str)):
            raise TypeError(
                f"StatValue '{self.key}' value must have type float, integer or string, not {type(self.value).__name__}."
            )

    def __repr__(self):
        return f"StatValue(key={self.key!r}, value={self.value!r})"


class Column:
    """Model a column of a dataset."""

    def __init__(
        self,
        name: str,
        data_type: str,
        stats: list[StatValue] | None = None,
        category_type: ColumnCategoryType | None = None,
    ):
        """Initialize a column.

        Parameters:
            name: The name of the column.
            data_type: The type of the data contained in the column.
            stats: Additional statistics about the column.
            category_type: Column category type.
        """
        self.name = name
        self.data_type = data_type
        self.stats = stats
        self.category_type = category_type

    def asdict(self) -> dict:
        obj = {
            "name": self.name,
            "dataType": self.data_type,
            "stats": [vars(stat) for stat in self.stats or []],
        }
        if self.category_type:
            obj["categoryType"] = self.category_type.value

        return obj


class DBColumn(Column):
    """Model a column of a dataset, like a database column."""

    def __init__(
        self,
        name: str,
        data_type: str,
        is_unique: bool | None = None,
        nullable: bool | None = None,
        is_private_key: bool | None = None,
        is_foreign_key: bool | None = None,
        stats: list[StatValue] | None = None,
    ):
        """Initialize a column.

        Parameters:
            name: The name of the column.
            data_type: The type of the data contained in the column.
            is_unique: If the column uniquely defines a record.
            nullable: If the column can contain null value.
            is_private_key: If the column uniquely defines a record,
                individually or with other columns (can be null).
            is_foreign_key: If the column refers to another one,
                individually or with other columns (cannot be null).
            stats: Additional statistics about the column.
        """
        super().__init__(name, data_type, stats)
        self.is_unique = is_unique
        self.nullable = nullable
        self.is_private_key = is_private_key
        self.is_foreign_key = is_foreign_key

    def asdict(self) -> dict:
        return {
            **super().asdict(),
            "isUnique": self.is_unique,
            "nullable": self.nullable,
            "isPK": self.is_private_key,
            "isFK": self.is_foreign_key,
        }
