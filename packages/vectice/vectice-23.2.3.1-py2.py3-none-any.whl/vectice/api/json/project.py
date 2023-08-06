from __future__ import annotations

from vectice.api.json.workspace import WorkspaceOutput


class ProjectInput(dict):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def description(self) -> str:
        return str(self["description"])


class ProjectOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "workspace" in self:
            self._workspace: WorkspaceOutput = WorkspaceOutput(**self["workspace"])

    @property
    def id(self) -> str:
        return str(self["vecticeId"])

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def description(self) -> str | None:
        if "description" in self and self["description"] is not None:
            return str(self["description"])
        else:
            return None

    @property
    def workspace(self) -> WorkspaceOutput:
        return self._workspace
