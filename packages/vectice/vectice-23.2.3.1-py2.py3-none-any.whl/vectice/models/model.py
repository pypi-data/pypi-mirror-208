from __future__ import annotations

import logging
import pickle  # nosec
from typing import Any

from vectice.models import Metric, Property
from vectice.models.dataset import TDerivedFrom, _get_derived_from

_logger = logging.getLogger(__name__)


class Model:
    """Represent a wrapped model.

    Iteration steps that represent models require a wrapped model.
    Wrapped models present Vectice with a learned predictor and
    appropriate metadata about that predictor in order to summarize
    the model in views of the iteration.
    """

    def __init__(
        self,
        library: str,
        technique: str,
        metrics: dict[str, int] | list[Metric] | Metric | None = None,
        properties: dict[str, str] | dict[str, int] | list[Property] | Property | None = None,
        name: str | None = None,
        attachments: str | list[str] | None = None,
        predictor: Any = None,
        derived_from: list[TDerivedFrom] | None = None,
    ):
        """Wrap a model (predictor).

        A Vectice Model is a wrapped predictor suitable for assignment
        to a Vectice Step.

        Parameters:
            library: The library used to generate the model.
            technique: The modeling technique used.
            metrics: A dict for example `{"MSE": 1}`.
            properties: A dict, for example `{"folds": 32}`.
            name: The model name. If None, will be auto-generated based on the library and technique.
            attachments: Path of a file that will be attached to the step along with the predictor.
            predictor: The predictor.
            derived_from: List of dataset (or version ids) to link as lineage.
        """
        self._library = library
        self._technique = technique
        self._name = name if name else self._generate_name()
        self._metrics = self._format_metrics(metrics) if metrics else None
        self._properties = self._format_properties(properties) if properties else None
        self._attachments = self._format_attachments(attachments) if attachments else None
        self._predictor = pickle.dumps(predictor)  # nosec
        self._derived_from = _get_derived_from(derived_from)

    def __repr__(self):
        return (
            f"Model(name='{self.name}', library='{self.library}', technique='{self.technique}', "
            f"metrics={self.metrics}, properties={self.properties}, attachments={self.attachments})"
        )

    @property
    def name(self) -> str:
        """The model's name.

        Returns:
            The model's name.
        """
        return self._name

    @name.setter
    def name(self, name):
        """Set the model's name.

        Parameters:
            name: The name of the model.
        """
        self._name = name

    @property
    def predictor(self) -> Any:
        """The model's predictor.

        Returns:
            The model's predictor.
        """
        return pickle.loads(self._predictor)  # noqa: S301

    @predictor.setter
    def predictor(self, predictor: Any):
        """Set the model's predictor.

        Parameters:
            predictor: The predictor of the model.
        """
        self._predictor = pickle.dumps(predictor)

    @classmethod
    def read_predictor_file(cls, path: str) -> Any:
        with open(path, "rb") as fh:
            return pickle.load(fh)  # noqa: S301

    @property
    def library(self) -> str:
        """The name of the library used to generate the model.

        Returns:
            The name of the library used to generate the model.
        """
        return self._library

    @library.setter
    def library(self, library):
        """Set the name of the library used to create the model.

        Parameters:
            library: The name of the library used to create the model.
        """
        self._library = library

    @property
    def technique(self) -> str:
        """The name of the modeling technique used to learn the model.

        Returns:
            The name of the modeling technique used to learn the model.
        """
        return self._technique

    @technique.setter
    def technique(self, technique):
        """Set the name of the modeling technique used to learn the model.

        Parameters:
            technique: The modeling technique used.
        """
        self._technique = technique

    @property
    def metrics(self) -> list[Metric] | None:
        """The model's metrics.

        Returns:
            The model's metrics.
        """
        return self._metrics

    @metrics.setter
    def metrics(self, metrics: dict[str, int] | list[Metric] | Metric | None):
        """Set the model's metrics.

        Parameters:
            metrics: The metrics of the model.
        """
        self._format_metrics(metrics)

    @property
    def properties(self) -> list[Property] | None:
        """The model's properties.

        Returns:
            The model's properties.
        """
        return self._properties

    @properties.setter
    def properties(self, properties: dict[str, str] | list[Property] | Property | None):
        """Set the model's properties.

        Parameters:
            properties: The properties of the model.
        """
        self._format_properties(properties)

    @property
    def attachments(self) -> list[str] | None:
        """The attachments associated with the model.

        Returns:
            The attachments associated with the model.
        """
        return self._attachments

    @attachments.setter
    def attachments(self, attachments: list[str] | str):
        """Attach a file or files to the model.

        Parameters:
            attachments: The filename or filenames of the file or set of files to attach to the model.
        """
        self._attachments = self._format_attachments(attachments)

    @property
    def derived_from(self) -> list[str]:
        """The datasets from which this model is derived.

        Returns:
            The datasets from which this model is derived.
        """
        return self._derived_from

    def _generate_name(self) -> str:
        return f"{self.library} {self.technique} model"

    def _format_metrics(self, metrics: dict[str, int] | list[Metric] | Metric | None) -> list[Metric]:
        if metrics is None:
            return []
        if isinstance(metrics, Metric):
            return [metrics]
        if isinstance(metrics, list):
            metrics = self._remove_incorrect_metrics(metrics)
            key_list = [metric.key for metric in metrics]
            self._check_key_duplicates(key_list)
            return metrics
        if isinstance(metrics, dict):
            return [Metric(key, value) for (key, value) in metrics.items()]
        else:
            raise ValueError("Please check metric type.")

    @staticmethod
    def _check_key_duplicates(key_list: list[str]):
        if len(key_list) != len(set(key_list)):
            raise ValueError("Duplicate keys are not allowed.")

    @staticmethod
    def _remove_incorrect_metrics(metrics: list[Metric]) -> list[Metric]:
        for metric in metrics:
            if not isinstance(metric, Metric):
                logging.warning(f"Incorrect metric '{metric}'. Please check metric type.")
                metrics.remove(metric)
        return metrics

    @staticmethod
    def _format_attachments(attachments: str | list[str]) -> list[str]:
        return [attachment for attachment in set(attachments)] if isinstance(attachments, list) else [attachments]

    def _format_properties(
        self, properties: dict[str, str] | dict[str, int] | list[Property] | Property | None
    ) -> list[Property]:
        if properties is None:
            return []
        if isinstance(properties, Property):
            return [properties]
        if isinstance(properties, list):
            properties = self._remove_incorrect_properties(properties)
            key_list = [prop.key for prop in properties]
            self._check_key_duplicates(key_list)
            return properties
        if isinstance(properties, dict):
            return [Property(key, str(value)) for (key, value) in properties.items()]
        else:
            raise ValueError("Please check property type.")

    @staticmethod
    def _remove_incorrect_properties(properties: list[Property]) -> list[Property]:
        for prop in properties:
            if not isinstance(prop, Property):
                logging.warning(f"Incorrect property '{prop}'. Please check property type.")
                properties.remove(prop)
        return properties
