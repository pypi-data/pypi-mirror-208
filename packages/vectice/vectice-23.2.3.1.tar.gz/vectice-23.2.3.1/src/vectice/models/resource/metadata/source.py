from __future__ import annotations

from pandas import DataFrame

from vectice.models.resource.metadata.column_metadata import Column
from vectice.models.resource.metadata.dataframe_column_parser import capture_columns


class Source:
    def __init__(
        self,
        name: str,
        size: int | None = None,
        columns: list[Column] | None = None,
        updated_date: str | None = None,
        created_date: str | None = None,
        dataframe: DataFrame | None = None,
    ):
        """Initialize a MetadataDB instance.

        Parameters:
            name: The name of the source.
            size: The size of the source.
            columns: The columns that compose the source.
            updated_date: The date of last update of the source.
            created_date: The date of last update of the source.
            dataframe: A pandas dataframe which will capture the sources metadata.
        """
        self.name = name
        self.size = size
        self.columns = columns
        self.created_date = created_date
        self.updated_date = updated_date
        self._dataframe = dataframe
        if dataframe is not None:
            size = dataframe.size
            self.size = float(size) if isinstance(size, float) else int(size)  # type: ignore[arg-type]

    def asdict(self) -> dict:
        return {
            "name": self.name,
            "size": self.size,
            "updatedDate": self.updated_date,
            "createdDate": self.created_date,
            "columns": capture_columns(init_columns=self.columns, dataframe=self._dataframe),
        }
