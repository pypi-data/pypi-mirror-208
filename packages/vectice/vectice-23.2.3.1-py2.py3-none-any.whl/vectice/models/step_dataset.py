from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.api.json.step import StepType
from vectice.models.step import Step

if TYPE_CHECKING:
    from vectice.api.json.iteration import IterationStepArtifact


class StepDataset(Step):
    """Model a dataset step.

    A dataset step stores a dataset version id.
    See also [`Dataset`][vectice.models.dataset.Dataset].
    """

    def __init__(self, step: Step, dataset_version: IterationStepArtifact):
        """Initialize a dataset step.

        Parameters:
            step: The step.
            dataset_version: The step's dataset version.
        """
        super().__init__(
            step.id,
            step._iteration,
            step.name,
            step.index,
            step.slug,
            step._description,
            step_type=StepType.StepDataset,
            artifacts=step.artifacts,
        )
        self._dataset_version = dataset_version

    def __repr__(self):
        return f"StepDataset(name={self.name!r}, id={self.id!r}, description={self._description!r}, dataset_version_id={self.dataset_version!r})"

    @property
    def dataset_version(self) -> IterationStepArtifact:
        """The step's dataset.

        Returns:
            The step's dataset.
        """
        return self._dataset_version
