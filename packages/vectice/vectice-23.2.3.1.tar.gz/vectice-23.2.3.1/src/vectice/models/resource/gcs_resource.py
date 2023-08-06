from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pandas import DataFrame

from vectice.models.resource.base import Resource
from vectice.models.resource.metadata import DatasetSourceOrigin
from vectice.models.resource.metadata.files_metadata import File, FilesMetadata

if TYPE_CHECKING:
    from google.cloud.storage import Blob, Bucket, Client

GS_URI_REG = r"(gs:\/\/)([^\/]+)\/(.+)"


class GCSResource(Resource):
    """GCS resource reference wrapper.

    This resource wraps GCS uris references such as file folders that you have stored in Google Cloud
    Storage with optional metadata and versioning. You assign it to a step.

    ```python
    from vectice import GCSResource

    gcs_resource = GCSResource(
        uris="gs://<bucket_name>/<file_path_inside_bucket>",
    )
    ```
    """

    _origin = DatasetSourceOrigin.GCS.value

    def __init__(
        self,
        uris: str | list[str],
        dataframes: DataFrame | list[DataFrame] | None = None,
        gcs_client: Client | None = None,
    ):
        """Initialize a GCS resource.

        Parameters:
            uris: The uris of the referenced resources. Should follow the pattern 'gs://<bucket_name>/<file_path_inside_bucket>'
            dataframes (Optional): The pandas dataframes allowing vectice to optionally compute more metadata about this resource such as columns stats.
            gcs_client (Optional): The `google.cloud.storage.Client` to optionally retrieve file size, creation date and updated date (used for auto-versioning).
        """
        super().__init__(paths=uris, dataframes=dataframes)
        self.gcs_client = gcs_client

        for uri in self._paths:
            if not re.search(GS_URI_REG, uri):
                raise ValueError(
                    f"Uri '{uri}' is not following the right pattern 'gs://<bucket_name>/<file_path_inside_bucket>'"
                )

    def _fetch_data(self) -> dict[str, bytes | None]:
        datas = {}
        for uri in self._paths:
            bucket_name, path = self._get_bucket_and_path_from_uri(uri)
            blobs = self._get_blobs(bucket_name, path)
            if blobs is not None:
                for blob in blobs:
                    datas[f"{bucket_name}/{path}"] = blob.download_as_bytes() if blob else None
        return datas

    def _build_metadata(self) -> FilesMetadata:
        files = []
        size: int | None = None
        df_index = 0
        for uri in self._paths:
            bucket_name, path = self._get_bucket_and_path_from_uri(uri)
            blobs = self._get_blobs(bucket_name, path)
            if blobs is not None:
                sorted_blobs = sorted(blobs, key=lambda bl: str(bl.name).lower())
                for blob in sorted_blobs:
                    dataframe = (
                        self._dataframes[df_index]
                        if self._dataframes is not None and len(self._dataframes) > df_index
                        else None
                    )
                    blob_file = self._build_file_from_blob(blob, f"gs://{bucket_name}", dataframe)
                    files.append(blob_file)
                    if size is None and blob_file.size is not None:
                        size = 0
                    if size is not None:
                        size += blob_file.size or 0
                    df_index += 1
            else:
                dataframe = (
                    self._dataframes[df_index]
                    if self._dataframes is not None and len(self._dataframes) > df_index
                    else None
                )
                files.append(File(name=path, uri=uri, dataframe=dataframe))
                df_index += 1
        metadata = FilesMetadata(
            size=size,
            origin=self._origin,
            files=files,
        )
        return metadata

    def _get_blobs(self, bucket_name, path: str) -> list[Blob] | None:
        from google.cloud import storage

        if self.gcs_client is None:
            return None

        bucket: Bucket = storage.Bucket(self.gcs_client, name=bucket_name)
        blob = self._recurse_blob(bucket, path)
        return self._get_children_blobs(self.gcs_client, bucket_name, blob)

    def _recurse_blob(self, bucket: Bucket, path: str) -> Blob:
        blob = bucket.get_blob(blob_name=path)
        if blob is None:
            if path.endswith("/"):
                raise NoSuchGCSResourceError(bucket.name, path)
            return self._recurse_blob(bucket, f"{path}/")
        return blob

    def _get_children_blobs(self, gcs_client: Client, bucket_name: str, blob: Blob) -> list[Blob]:
        path: str = blob.name
        if path.endswith("/"):
            all_blobs: list[Blob] = []
            blobs: list[Blob] = gcs_client.list_blobs(bucket_or_name=bucket_name, prefix=path)
            for bl in blobs:
                if bl.name.endswith("/") is False:
                    bl.reload()
                    all_blobs.append(bl)
            return all_blobs
        blob.reload()
        return [blob]

    def _build_file_from_blob(self, blob: Blob, uri: str, dataframe: DataFrame | None = None) -> File:
        return File(
            name=blob.name,
            size=blob.size,
            fingerprint=blob.md5_hash,
            created_date=blob.time_created.isoformat(),
            updated_date=blob.updated.isoformat(),
            uri=f"{uri}/{blob.name}",
            dataframe=dataframe,
        )

    def _get_bucket_and_path_from_uri(self, uri: str) -> tuple[str, str]:
        match = re.search(GS_URI_REG, uri)
        if match is not None:
            _, bucket_name, path = match.groups()
            return bucket_name, path

        raise ValueError(
            f"Uri '{uri}' is not following the right pattern 'gs://<bucket_name>/<file_path_inside_bucket>'"
        )


class NoSuchGCSResourceError(Exception):
    def __init__(self, bucket: str, resource: str):
        self.message = f"{resource} does not exist in the GCS bucket {bucket}."
        super().__init__(self.message)
