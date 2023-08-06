from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


def existing_dataset_logger(data: dict, dataset_name: str, _logger: Logger) -> str | None:
    """Identifies if the dataset and it's version exists already."""
    if data["useExistingDataset"]:
        existing_dataset_version = f"Dataset: {dataset_name}"
        if data["useExistingVersion"]:
            existing_dataset_version += f" with Version: {data['datasetVersion']['name']}"
        _logger.debug(f"{existing_dataset_version} already exists.")
        return existing_dataset_version
    return None


def existing_model_logger(data: dict, model_name: str, _logger: Logger):
    if data["useExistingModel"]:
        existing_model = f"Model: {model_name} already exists."
        _logger.debug(existing_model)
        return existing_model
    return
