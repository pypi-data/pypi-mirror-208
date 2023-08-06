from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pandas import DataFrame

from vectice.models.resource.base import Resource
from vectice.models.resource.metadata.base import DatasetSourceOrigin
from vectice.models.resource.metadata.files_metadata import File, FilesMetadata

if TYPE_CHECKING:
    from mypy_boto3_s3 import Client
    from mypy_boto3_s3.type_defs import ListObjectsV2OutputTypeDef, ObjectTypeDef


S3_URI_REG = r"(s3:\/\/)([^\/]+)\/(.+)"


class S3Resource(Resource):
    """AWS S3resource reference wrapper.

    This resource wraps AWS S3 uris references such as file folders that you have stored in AWS S3
    with optional metadata and versioning. You assign it to a step.

    ```python
    from vectice import S3Resource

    s3_resource = S3Resource(
        uris="s3://<bucket_name>/<file_path_inside_bucket>",
    )
    ```
    """

    _origin = DatasetSourceOrigin.S3.value

    def __init__(
        self,
        uris: str | list[str],
        dataframes: DataFrame | list[DataFrame] | None = None,
        s3_client: Client | None = None,
    ):
        """Initialize an S3 resource.

        Parameters:
            uris: The uris of the resources to get. Should follow the pattern 's3://<bucket_name>/<file_path_inside_bucket>'
            dataframes (Optional): The pandas dataframes allowing vectice to optionally compute more metadata about this resource such as columns stats.
            s3_client (Optional): The Amazon s3 client to optionally retrieve file size, creation date and updated date (used for auto-versioning).
        """
        super().__init__(paths=uris, dataframes=dataframes)
        self.s3_client = s3_client

        for uri in self._paths:
            if not re.search(S3_URI_REG, uri):
                raise ValueError(
                    f"Uri '{uri}' is not following the right pattern 's3://<bucket_name>/<file_path_inside_bucket>'"
                )

    def _fetch_data(self) -> dict[str, bytes | None]:
        datas = {}
        if self.s3_client:
            s3_objects_list = self._get_s3_objects_list(self.s3_client)
            for bucket_name, s3_objects in s3_objects_list:
                for s3_object in s3_objects["Contents"]:
                    object_path = s3_object["Key"]
                    data = self._get_aws_data(self.s3_client, bucket_name, object_path)
                    datas[f"{bucket_name}/{object_path}"] = data
        else:
            for path in self._paths:
                datas[path] = None

        return datas

    def _get_aws_data(self, s3_client: Client, bucket_name: str, object_path: str):
        data_response = s3_client.get_object(Bucket=bucket_name, Key=object_path)
        return data_response["Body"].read()

    def _build_metadata(self) -> FilesMetadata:
        size = None
        files = []
        df_index = 0
        if self.s3_client:
            s3_objects_list = self._get_s3_objects_list(self.s3_client)
            for bucket_name, s3_objects in s3_objects_list:
                if s3_objects["KeyCount"] == 0:
                    raise NoSuchS3ResourceError(bucket_name, s3_objects["Prefix"])
                s3_object = s3_objects["Contents"]
                new_files, total_size, new_df_index = self._build_files_list_with_size(
                    index=df_index, bucket_name=bucket_name, s3_object=s3_object
                )
                if size is None:
                    size = 0
                size += total_size
                files.extend(new_files)
                df_index += new_df_index
        else:
            for index, uri in enumerate(self._paths):
                dataframe = (
                    self._dataframes[index] if self._dataframes is not None and len(self._dataframes) > index else None
                )
                _, path = self._get_bucket_and_path_from_uri(uri)
                file = File(name=path, uri=uri, dataframe=dataframe)
                files.append(file)

        metadata = FilesMetadata(files=files, origin=self._origin, size=size)
        return metadata

    def _build_files_list_with_size(
        self, index: int, bucket_name: str, s3_object: list[ObjectTypeDef]
    ) -> tuple[list[File], int, int]:
        files: list[File] = []
        total_size = 0
        df_index = 0
        filtered_s3_object = list(filter(lambda obj: self._is_s3_object_a_folder(obj) is False, s3_object))
        sorted_s3_object = sorted(filtered_s3_object, key=lambda obj: obj["Key"].lower())
        for object in sorted_s3_object:
            new_index = df_index + index
            name = object["Key"]
            size = object["Size"]
            uri = f"s3://{bucket_name}/{name}"
            dataframe = (
                self._dataframes[new_index]
                if self._dataframes is not None and len(self._dataframes) > new_index
                else None
            )

            file = File(
                name=name,
                size=size,
                fingerprint=self._get_formatted_etag_from_object(object),
                updated_date=object["LastModified"].isoformat(),
                created_date=None,
                uri=uri,
                dataframe=dataframe,
            )
            total_size += size
            files.append(file)
            df_index += 1
        return files, total_size, df_index

    def _get_s3_objects_list(self, s3_client: Client) -> list[tuple[str, ListObjectsV2OutputTypeDef]]:
        return list(map(lambda uri: self._get_s3_objects(s3_client, uri), self._paths))

    def _get_s3_objects(self, s3_client: Client, uri: str) -> tuple[str, ListObjectsV2OutputTypeDef]:
        bucket_name, path = self._get_bucket_and_path_from_uri(uri)
        return bucket_name, s3_client.list_objects_v2(Bucket=bucket_name, Prefix=path)

    def _get_bucket_and_path_from_uri(self, uri: str) -> tuple[str, str]:
        match = re.search(S3_URI_REG, uri)
        if match is not None:
            _, bucket_name, path = match.groups()
            return bucket_name, path

        raise ValueError(
            f"Uri '{uri}' is not following the right pattern 's3://<bucket_name>/<file_path_inside_bucket>'"
        )

    @staticmethod
    def _get_formatted_etag_from_object(object: ObjectTypeDef) -> str:
        return str(object["ETag"].replace("'", "").replace('"', ""))

    @staticmethod
    def _is_s3_object_a_folder(object: ObjectTypeDef) -> bool:
        return bool(object["Key"].endswith("/"))


class NoSuchS3ResourceError(Exception):
    def __init__(self, bucket: str, resource: str):
        self.message = f"{resource} does not exist in the AWS s3 bucket {bucket}."
        super().__init__(self.message)
