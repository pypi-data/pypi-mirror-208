from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pandas import DataFrame

from vectice.models.resource.base import Resource
from vectice.models.resource.metadata import DatasetSourceOrigin
from vectice.models.resource.metadata.column_metadata import DBColumn
from vectice.models.resource.metadata.db_metadata import DBMetadata, MetadataDB

if TYPE_CHECKING:
    from google.cloud.bigquery import Client as BQClient
    from google.cloud.bigquery import Table

_logger = logging.getLogger(__name__)


class BigQueryResource(Resource):
    """BigQuery resource reference wrapper.

    This resource wraps BigQuery paths that you have stored in BigQuery with optional metadata and versioning. You assign it to a step.

    ```python
    from vectice import BigQueryResource

    bq_resource = BigQueryResource(
        paths="bigquery-public-data.stackoverflow.posts_questions",
    )
    ```
    """

    _origin = DatasetSourceOrigin.BIGQUERY.value

    def __init__(
        self,
        paths: str | list[str],
        dataframes: DataFrame | list[DataFrame] | None = None,
        bq_client: BQClient | None = None,
    ):
        """Initialize a BigQuery resource.

        Parameters:
            paths: The paths to retrieve the datasets or the tables.
            dataframes (Optional): The pandas dataframes allowing vectice to optionally compute more metadata about this resource such as columns stats.
            bq_client (Optional): The `google.cloud.bigquery.Client` to optionally retrieve file size, creation date and updated date (used for auto-versioning).
        """
        super().__init__(paths=paths, dataframes=dataframes)
        self.bq_client = bq_client

    def _fetch_data(self) -> dict[str, tuple[Table | None, DataFrame | None]]:
        tables: dict[str, tuple[Table | None, DataFrame | None]] = {}
        df_index = 0
        for path in self._paths:
            path_tables, new_df_index = self._fetch_path_data(index=df_index, path=path)
            tables.update(path_tables)
            df_index += new_df_index

        return tables

    def _fetch_path_data(self, index: int, path: str) -> tuple[dict[str, tuple[Table | None, DataFrame | None]], int]:
        count_dots_in_path = path.count(".")
        is_dataset = count_dots_in_path == 1
        is_table = count_dots_in_path == 2

        if is_table is True:
            return self._fetch_table_data(index=index, path=path), 1

        if is_dataset is True:
            return self._fetch_dataset_data(index=index, path=path)

        raise ValueError(f"Path '{path}' is invalid, please reference either a dataset or a table.")

    def _fetch_table_data(self, index: int, path: str) -> dict[str, tuple[Table | None, DataFrame | None]]:
        from google.api_core.exceptions import Forbidden

        table_name = path.partition(".")[-1]

        dataframe = self._dataframes[index] if self._dataframes is not None and len(self._dataframes) > index else None
        if self.bq_client is None:
            return {table_name: (None, dataframe)}

        tb = None
        try:
            tb = self.bq_client.get_table(table=path)
        except Forbidden:
            _logger.warning(f"Failed to fetch data information for table {table_name}")
            pass

        return {table_name: (tb, dataframe)}

    def _fetch_dataset_data(
        self, index: int, path: str
    ) -> tuple[dict[str, tuple[Table | None, DataFrame | None]], int]:
        from google.api_core.exceptions import Forbidden

        df_index = 0
        tables_dict: dict[str, tuple[Table | None, DataFrame | None]] = {}
        dataset = path.partition(".")[-1]
        if self.bq_client is None:
            new_index = df_index + index
            dataframe = (
                self._dataframes[new_index]
                if self._dataframes is not None and len(self._dataframes) > new_index
                else None
            )
            return {dataset: (None, dataframe)}, 1
        try:
            tables_data: list[Table] = self.bq_client.list_tables(dataset=path)  # type: ignore[assignment]
            tables = sorted(tables_data, key=lambda table: table.table_id.lower())
            for table in tables:
                new_index = df_index + index
                dataframe = (
                    self._dataframes[new_index]
                    if self._dataframes is not None and len(self._dataframes) > new_index
                    else None
                )
                dataset = path.partition(".")[-1]
                table_name = f"{dataset}.{table.table_id}"
                try:
                    tables_dict[table_name] = (
                        self.bq_client.get_table(table=f"{path}.{table.table_id}"),
                        dataframe,
                    )
                except Exception:
                    _logger.warning(f"Failed to fetch data information for table {table_name}")
                    tables_dict[table_name] = None, dataframe
                    pass

                df_index += 1
            return tables_dict, df_index
        except Forbidden:
            _logger.warning(f"Failed to list tables for dataset {path}")
            return {}, 0

    def _build_metadata(self) -> DBMetadata:
        tables_metadata: dict[str, tuple[Table | None, DataFrame | None]] = self.data  # type:ignore[assignment]
        dbs: list[MetadataDB] = []
        for table_name, [table_metadata, dataframe] in tables_metadata.items():
            columns: list[DBColumn] = []
            size = None
            rows_number = None
            updated_date = None
            created_date = None
            if table_metadata is not None:
                size = table_metadata.num_bytes
                rows_number = table_metadata.num_rows
                modified = table_metadata.modified
                updated_date = modified.isoformat() if modified is not None else None
                created = table_metadata.created
                created_date = created.isoformat() if created is not None else None
                for column in table_metadata.schema:
                    columns.append(
                        DBColumn(
                            name=column.name,
                            data_type=column.field_type,
                            is_unique=False,
                            nullable=column.is_nullable,
                            is_private_key=False,
                            is_foreign_key=False,
                        )
                    )

            dbs.append(
                MetadataDB(
                    name=table_name,
                    rows_number=rows_number,
                    size=size,
                    columns=columns,
                    created_date=created_date,
                    updated_date=updated_date,
                    dataframe=dataframe,
                )
            )

        metadata_size = None
        for db in dbs:
            if db.size is not None:
                if metadata_size is None:
                    metadata_size = 0
                metadata_size += db.size

        metadata = DBMetadata(
            size=metadata_size,
            origin=self._origin,
            dbs=dbs,
        )
        return metadata
