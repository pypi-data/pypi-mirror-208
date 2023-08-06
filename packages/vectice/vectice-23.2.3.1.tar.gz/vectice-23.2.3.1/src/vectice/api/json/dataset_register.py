from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vectice.api.json.dataset_version import DatasetVersionOutput
    from vectice.models.property import Property
    from vectice.models.resource.metadata import FilesMetadata, MetadataDB


class DatasetRegisterOutput(dict):
    @property
    def dataset_version(self) -> DatasetVersionOutput:
        from vectice.api.json.dataset_version import DatasetVersionOutput

        return DatasetVersionOutput(**self["datasetVersion"])

    @property
    def use_existing_version(self) -> bool:
        return bool(self["useExistingVersion"])

    @property
    def use_existing_dataset(self) -> bool:
        return bool(self["useExistingDataset"])

    # TODO: complete the jobrun property
    @property
    def job_run(self) -> str:
        return str(self["jobRun"])


class DatasetRegisterInput(dict):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def type(self) -> str:
        return str(self["type"])

    @property
    def data_sources(self) -> list[dict]:
        return list(self["datasetSources"])

    @property
    def derived_from(self) -> list[int]:
        return list(self["inputs"])

    @property
    def properties(self) -> Property:
        from vectice.models.property import Property

        return Property(**self["properties"])


class DatasetSourceInput(dict):
    @property
    def type(self) -> str:
        return str(self["type"])

    @property
    def usage(self) -> str:
        return str(self["usage"])

    @property
    def origin(self) -> str:
        return str(self["origin"])

    @property
    def size(self) -> int:
        return int(self["size"])

    @property
    def dbs(self) -> list[MetadataDB]:
        from vectice.models.resource.metadata import MetadataDB

        return [MetadataDB(**item) for item in self["dbs"]]

    @property
    def files(self) -> FilesMetadata:
        from vectice.models.resource.metadata import FilesMetadata

        return FilesMetadata(**self["files"])
