from __future__ import annotations

import logging

from vectice.api.json.iteration import IterationStepArtifactInput
from vectice.api.json.step import StepType
from vectice.models.step import Step
from vectice.utils.common_utils import _check_read_only

_logger = logging.getLogger(__name__)


class StepNumber(Step):
    """Model a Vectice step's number.

    A StepNumber stores numeric values.
    """

    def __init__(self, step: Step, number: int | float | None = None):
        """Initialize a number step.

        Parameters:
            step: The step.
            number: The step's number.
        """
        super().__init__(
            id=step.id,
            iteration=step._iteration,
            name=step.name,
            index=step.index,
            slug=step.slug,
            description=step._description,
            step_type=StepType.StepNumber,
            artifacts=step.artifacts,
        )
        self._number = number

    def __repr__(self):
        return (
            f"StepNumber(name={self.name!r}, id={self.id!r}, description={self._description!r}, number={self.number!r})"
        )

    @property
    def number(self) -> int | float | None:
        """The step's number.

        Returns:
            The step's number.
        """
        return self._number

    @number.setter
    def number(self, value: int | float) -> None:
        """Set the step's number.

        Typical usage example:

        ```pycon
        >>> my_iteration = my_phase.iteration()
        ... my_iteration.step_scoring = 21
        ```

        Parameters:
            value: The number.
        """
        _check_read_only(self.iteration)
        step_artifacts = [IterationStepArtifactInput(type="Comment", text=value)]
        self._client.update_iteration_step_artifact(
            self.id,
            StepType.StepNumber,
            step_artifacts,
        )
        self._number = value
