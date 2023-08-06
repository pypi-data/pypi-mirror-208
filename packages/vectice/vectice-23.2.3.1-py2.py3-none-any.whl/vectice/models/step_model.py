from __future__ import annotations

from typing import TYPE_CHECKING

from vectice.api.json.step import StepType
from vectice.models.step import Step

if TYPE_CHECKING:
    from vectice.api.json.iteration import IterationStepArtifact
    from vectice.models.model import Model


class StepModel(Step):
    """Model a model step.

    A model step stores a model version id.
    See also [`Dataset`][vectice.models.model.Model].
    """

    def __init__(self, step: Step, model_version: IterationStepArtifact, model: Model | None = None):
        """Initialize a dataset step.

        Parameters:
            step: The step.
            model_version: The step's model version.
        """
        super().__init__(
            step.id,
            step._iteration,
            step.name,
            step.index,
            step.slug,
            step._description,
            step_type=StepType.StepModel,
            artifacts=step.artifacts,
        )
        self._model_version = model_version
        self._model = model

    def __repr__(self):
        return f"StepModel(name={self.name!r}, id={self.id!r}, description={self._description!r}, model_version_id={self.model_version!r})"

    @property
    def model_version(self) -> IterationStepArtifact:
        """The step's model.

        Returns:
            The step's model.
        """
        return self._model_version
