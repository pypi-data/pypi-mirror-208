from __future__ import annotations

import logging

from vectice.api.json.iteration import IterationStepArtifactInput
from vectice.api.json.step import StepType
from vectice.models.step import Step
from vectice.utils.common_utils import _check_read_only

_logger = logging.getLogger(__name__)


class StepString(Step):
    """Model a string step."""

    def __init__(self, step: Step, string: str | None = None):
        """Initialize a string step.

        Parameters:
            step: The step.
            string: The step string.
        """
        super().__init__(
            step.id,
            step._iteration,
            step.name,
            step.index,
            step.slug,
            step._description,
            step_type=StepType.StepString,
            artifacts=step.artifacts,
        )
        self._string = string

    def __repr__(self):
        return f"StepString(name={self.name!r}, id={self.id!r}, description={self._description!r}, string={self._string!r})"

    @property
    def string(self) -> str | None:
        """The step's string.

        Returns:
            The step's string.
        """
        return self._string

    @string.setter
    def string(self, value: str) -> None:
        """Set the step's string.

        Typical usage example:

        ```pycon
        >>> my_iteration = my_phase.iteration()
        ... my_iteration.step_exploration = "Step information"
        ```

        Parameters:
            value: The string to set.
        """
        _check_read_only(self.iteration)
        step_artifacts = [IterationStepArtifactInput(type="Comment", text=value)]
        self._client.update_iteration_step_artifact(self.id, StepType.StepString, step_artifacts)
        self._string = value
