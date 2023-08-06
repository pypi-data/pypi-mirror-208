from __future__ import annotations

from vectice.models.resource.base import Resource
from vectice.models.resource.bigquery_resource import BigQueryResource
from vectice.models.resource.file_resource import File, FileResource, FilesMetadata
from vectice.models.resource.gcs_resource import GCSResource, NoSuchGCSResourceError
from vectice.models.resource.s3_resource import NoSuchS3ResourceError, S3Resource

__all__ = [
    "Resource",
    "FilesMetadata",
    "FileResource",
    "File",
    "GCSResource",
    "BigQueryResource",
    "NoSuchGCSResourceError",
    "S3Resource",
    "NoSuchS3ResourceError",
]
