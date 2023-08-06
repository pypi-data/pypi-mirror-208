from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from vectice.api.json.phase import PhaseOutput

if TYPE_CHECKING:
    from vectice.api.json.iteration import IterationStepArtifact


class DocumentationPageStatus(Enum):
    """Enumeration of the different statuses for documentation pages."""

    NotStarted = "NotStarted"
    InProgress = "Draft"
    Completed = "Completed"


class StepType(Enum):
    """Enumeration of the different types of steps."""

    Step = "UNKNOWN"
    StepDataset = "DATASET"
    StepModel = "MODEL"
    StepNumber = "NUMBER"
    StepString = "STRING"
    StepPlot = "PLOT"
    StepImage = "IMAGE"


class StepInput(dict):
    @property
    def id(self) -> int:
        return int(self["id"])

    @property
    def index(self) -> int:
        return int(self["index"])

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def completed(self) -> bool:
        return bool(self["completed"])

    @property
    def description(self) -> str | None:
        return str(self["description"])

    @property
    def artifacts(self) -> list[IterationStepArtifact]:
        # TODO: refactor to break cyclic import
        from vectice.api.json.iteration import IterationStepArtifact

        return [IterationStepArtifact(artifact) for artifact in self["artifacts"]]

    @property
    def step_type(self) -> StepType:
        return StepType(self["stepType"])


class StepOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "phase" in self:
            self._phase: PhaseOutput = PhaseOutput(**self["phase"])
        else:
            self._phase = None
        if "slug" in self:
            self["slug"] = f"step_{self['slug']}"

    @property
    def id(self) -> int:
        return int(self["id"])

    @property
    def index(self) -> int:
        return int(self["index"])

    @property
    def parent(self) -> PhaseOutput:
        return self._phase

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def completed(self) -> bool:
        return bool(self["completed"])

    @property
    def description(self) -> str | None:
        return str(self["description"])

    @property
    def slug(self) -> str:
        return str(self["slug"])

    @property
    def artifacts(self) -> list[IterationStepArtifact]:
        # TODO: refactor to break cyclic import
        from vectice.api.json.iteration import IterationStepArtifact

        return [IterationStepArtifact(artifact) for artifact in self["artifacts"]]

    @property
    def step_type(self) -> StepType:
        return StepType(self["stepType"])
