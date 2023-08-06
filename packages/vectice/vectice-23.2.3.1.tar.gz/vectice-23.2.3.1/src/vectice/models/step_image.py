from __future__ import annotations

import logging
from io import IOBase

from PIL import Image

from vectice.api.json.iteration import IterationStepArtifactInput
from vectice.api.json.step import StepType
from vectice.models.step import Step
from vectice.utils.common_utils import _check_read_only, _get_image_variables

_logger = logging.getLogger(__name__)


class StepImage(Step):
    """Model a Vectice step's image.

    A StepImage stores an image.
    """

    def __init__(self, step: Step, image: str | IOBase | None = None):
        """Initialize a step's image.

        Parameters:
            step: The step
            image: The step's image.
        """
        super().__init__(
            id=step.id,
            iteration=step._iteration,
            name=step.name,
            index=step.index,
            slug=step.slug,
            description=step._description,
            step_type=StepType.StepImage,
            artifacts=step.artifacts,
        )
        self._image: str | IOBase | None = image

    def __repr__(self):
        return f"StepImage(name='{self.name}', id={self.id}, description='{self._description}', image={self.image})"

    @property
    def image(self) -> str | IOBase | None:
        """The step's image.

        Returns:
            The step's image.
        """
        return self._image

    @image.setter
    def image(self, value: str | IOBase | Image.Image):
        """The step's image.

        Typical usage example with image path:

        ```python
        my_iteration = my_phase.iteration()
        my_iteration.step_explanation = "accuracy.png"
        ```

        Typical usage example with object in memory:

        ```python
        my_iteration = my_phase.iteration()
        with open("my_image.png", "rb") as image:
            my_iteration.step_explanation = image
        ```

        Typical usage example with PIL object in memory:

        ```python
        my_iteration = my_phase.iteration()
        with Image.open("my_image.png") as image:
            my_iteration.step_explanation = image
        ```

        Parameters:
            value: The image path or object.
        """
        _check_read_only(self.iteration)
        image, filename = _get_image_variables(value)
        self._image = filename
        attachments_output = self._client.create_phase_attachments(
            [("file", (filename, image))], self.phase.id, self.project.id
        )
        step_artifacts = [
            IterationStepArtifactInput(id=artifact["entityId"], type="EntityFile") for artifact in attachments_output
        ]
        self._client.update_iteration_step_artifact(
            self.id,
            StepType.StepImage,
            step_artifacts,
        )
