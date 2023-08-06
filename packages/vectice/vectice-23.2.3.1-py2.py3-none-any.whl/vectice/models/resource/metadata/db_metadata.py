from __future__ import annotations

from pandas import DataFrame

from vectice.models.resource.metadata.base import (
    DatasetSourceType,
    DatasetSourceUsage,
    Metadata,
)
from vectice.models.resource.metadata.column_metadata import DBColumn
from vectice.models.resource.metadata.source import Source


class DBMetadata(Metadata):
    """Class that describes metadata of dataset that comes from a database."""

    def __init__(
        self,
        dbs: list[MetadataDB],
        size: int | None,
        usage: DatasetSourceUsage | None = None,
        origin: str | None = None,
    ):
        """Initialize a DBMetadata instance.

        Parameters:
            dbs: The list of databases.
            size: The size of the metadata.
            usage: The usage of the metadata.
            origin: The origin of the metadata.
        """
        super().__init__(size=size, type=DatasetSourceType.DB, usage=usage, origin=origin)
        self.dbs = dbs

    def asdict(self) -> dict:
        return {
            **super().asdict(),
            "dbs": [db.asdict() for db in self.dbs],
        }


class MetadataDB(Source):
    def __init__(
        self,
        name: str,
        columns: list[DBColumn],
        rows_number: int | None = None,
        size: int | None = None,
        updated_date: str | None = None,
        created_date: str | None = None,
        dataframe: DataFrame | None = None,
    ):
        """Initialize a MetadataDB instance.

        Parameters:
            name: The name of the table.
            columns: The columns that compose the table.
            rows_number: The number of row of the table.
            size: The size of the table.
            updated_date: The date of last update of the table.
            created_date: The creation date of the table.
            dataframe: A pandas dataframe which will capture the tables metadata.
        """
        super().__init__(
            name=name,
            size=size,
            columns=list(columns),
            updated_date=updated_date,
            created_date=created_date,
            dataframe=dataframe,
        )
        self.rows_number = rows_number
        if dataframe is not None:
            self.rows_number = len(dataframe.index)

    def asdict(self) -> dict:
        return {
            **super().asdict(),
            "rowsNumber": self.rows_number,
        }
