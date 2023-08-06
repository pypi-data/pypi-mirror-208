from vectice.api.json.workspace import WorkspaceOutput


class UserOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UserAndDefaultWorkspaceOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def default_workspace(self) -> WorkspaceOutput:
        return WorkspaceOutput(**self["defaultWorkspace:"])

    @property
    def user(self) -> UserOutput:
        return UserOutput(**self["user"])
