from __future__ import annotations

import io
import logging
import os
from typing import TYPE_CHECKING, BinaryIO, List

from vectice.api.json.dataset_version import DatasetVersionOutput
from vectice.api.json.model_version import ModelVersionOutput

if TYPE_CHECKING:
    from vectice.api import Client

_logger = logging.getLogger(__name__)

FILE_PATH_DOES_NOT_EXIST_ERROR_MESSAGE = "The file path '%s' is not valid. The file does not exist."


class AttachmentContainer:
    def __init__(self, version: ModelVersionOutput | DatasetVersionOutput, client: Client):
        self._client = client
        self._version = version
        self._id = version.id
        self._name = version.name

    @property
    def version(self):
        return self._version

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    def add_attachments(self, file_paths: str | list[str]):
        """Add an attachment or set of attachments to the entity.

        Parameters:
            file_paths: The paths of the attachment(s).

        Returns:
            A list of dictionaries describing the attachments.
        """
        file_paths = [file_paths] if isinstance(file_paths, str) else file_paths
        attachments = self._add_files_to_attachments(file_paths)
        try:
            return self._client.create_version_attachments(attachments, self._version)
        finally:
            self._close_attached_files(attachments)

    def _add_files_to_attachments(self, file_paths: list[str]) -> list[tuple[str, tuple[str, BinaryIO]]]:
        attachments: List[tuple[str, tuple[str, BinaryIO]]] = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise ValueError(FILE_PATH_DOES_NOT_EXIST_ERROR_MESSAGE % file_path)
            curr_file = ("file", (file_path, open(file_path, "rb")))
            attachments.append(curr_file)
        return attachments

    def _close_attached_files(self, attachments: list[tuple[str, tuple[str, BinaryIO]]]) -> None:
        for attachment in attachments:
            attachment[1][1].close()

    def add_serialized_model(self, model_type: str, model_content: bytes):
        if isinstance(self._version, ModelVersionOutput):
            self._client.create_model_predictor(model_type, io.BytesIO(model_content), self._version)
