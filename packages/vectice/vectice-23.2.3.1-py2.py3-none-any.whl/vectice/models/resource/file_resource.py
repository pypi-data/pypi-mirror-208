from __future__ import annotations

import datetime
import glob
import hashlib
import logging
import os

from pandas import DataFrame

from vectice.models.resource.base import Resource
from vectice.models.resource.metadata.base import DatasetSourceOrigin
from vectice.models.resource.metadata.files_metadata import File, FilesMetadata

_logger = logging.getLogger(__name__)


class FileResource(Resource):
    """Wrap columnar data and its metadata in a local file.

    Vectice stores metadata -- data about your dataset -- communicated
    with a resource.  Your actual dataset is not stored by Vectice.

    This resource wraps data that you have stored in a local file.

    ```python
    from vectice import FileResource, connect

    my_project = connect(...)  # (1)
    my_phase = my_project.phase(...)  # (2)
    my_iter = my_phase.iteration()  # (3)

    my_iter.step_my_data = FileResource(paths="my/file/path")
    ```

    1. See [connection][vectice.Connection.connect].
    1. See [phases][vectice.models.Phase].
    1. See [iterations][vectice.models.Iteration].

    Note that these three concepts are distinct, even if easily conflated:

    * Where the data is stored
    * The format at rest (in storage)
    * The format when loaded in a running Python program

    Notably, the statistics collectors provided by Vectice operate
    only on this last and only in the event that the data is loaded as
    a pandas dataframe.
    """

    _origin = DatasetSourceOrigin.LOCAL.value

    def __init__(
        self,
        paths: str | list[str],
        dataframes: DataFrame | list[DataFrame] | None = None,
    ):
        """Initialize a file resource.

        Parameters:
            paths: The paths of the files to wrap.
            dataframes: The pandas dataframes allowing vectice to compute more metadata about this resource.

        Examples:
            The following example shows how to wrap a CSV file
            called `iris.csv` in the current directory:

            ```python
            from vectice import FileResource
            iris_trainset = FileResource(paths="iris.csv")
            ```
        """
        super().__init__(paths=paths, dataframes=dataframes)
        paths_log = ", ".join(self._paths) if len(self._paths) > 1 else self._paths[0]
        _logger.info(f"File: {paths_log} wrapped successfully.")

    def _fetch_data(self) -> dict[str, bytes]:
        datas = {}
        metadata: FilesMetadata = self.metadata  # type:ignore[assignment]
        for file in metadata.files:
            with open(file.name, "rb") as opened_file:
                datas[file.name] = opened_file.read()
        return datas

    def _build_metadata(self) -> FilesMetadata:
        if self._paths is None:
            raise ValueError("Paths can not be None.")
        size = None
        files = []
        df_index = 0
        for path in self._paths:
            new_files, total_size, new_df_index = self._file_visitor_list_builder(index=df_index, path=path)
            df_index += new_df_index
            if size is None:
                size = 0
            size += total_size
            files.extend(new_files)

        metadata = FilesMetadata(size=size, origin=self._origin, files=files)
        return metadata

    def _file_visitor_list_builder(self, index: int, path: str) -> tuple[list[File], int, int]:
        files: list[File] = []
        total_size = 0
        df_index = 0
        if not os.path.exists(path):
            raise FileNotFoundError
        if os.path.isfile(path):
            dataframe = (
                self._dataframes[index] if self._dataframes is not None and len(self._dataframes) > index else None
            )
            file: File = self._build_file_from_path(path=path, dataframe=dataframe)
            total_size += file.size or 0
            files.append(file)
            df_index += 1
        else:
            dir_paths = glob.glob(f"{path}/**", recursive=True)
            for entry_path in filter(lambda x: os.path.isfile(x), sorted(dir_paths, key=str.lower)):
                new_index = index + df_index
                dataframe = (
                    self._dataframes[new_index]
                    if self._dataframes is not None and len(self._dataframes) > new_index
                    else None
                )
                glob_file: File = self._build_file_from_path(path=entry_path, dataframe=dataframe)
                total_size += glob_file.size or 0
                files.append(glob_file)
                df_index += 1
        return files, total_size, df_index

    def _build_file_from_path(self, path: str, dataframe: DataFrame | None = None) -> File:
        entry_stats: os.stat_result = os.stat(path)
        name = path.split("\\")[-1]
        return File(
            name=name,
            size=entry_stats.st_size,
            fingerprint=self._compute_digest_for_path(path),
            updated_date=self._convert_date_to_iso(entry_stats.st_mtime),
            uri=f"file://{os.path.abspath(path)}",
            dataframe=dataframe,
        )

    @staticmethod
    def _compute_digest_for_path(path: str) -> str:
        sha = hashlib.sha256()
        bytes_array = bytearray(128 * 1024)
        mv = memoryview(bytes_array)
        with open(path, "rb", buffering=0) as file:
            n = file.readinto(mv)
            while n:
                sha.update(mv[:n])
                n = file.readinto(mv)
        return sha.hexdigest()

    @staticmethod
    def _convert_date_to_iso(timestamp: float) -> str:
        return datetime.datetime.fromtimestamp(timestamp).isoformat()
