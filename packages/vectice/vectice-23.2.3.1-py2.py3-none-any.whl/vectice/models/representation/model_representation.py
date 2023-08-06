from vectice.api.json.model_representation import ModelRepresentationOutput
from vectice.models.representation.model_version_representation import ModelVersionRepresentation


class ModelRepresentation:
    def __init__(self, output: ModelRepresentationOutput):
        self.id = output.id
        self.project_id = output.project_id
        self.name = output.name
        self.type = output.type
        self.description = output.description
        self.version = ModelVersionRepresentation(output.version)
