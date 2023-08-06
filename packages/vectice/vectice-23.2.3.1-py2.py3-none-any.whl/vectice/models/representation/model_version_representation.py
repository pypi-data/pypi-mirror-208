from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput


class ModelVersionRepresentation:
    def __init__(self, output: ModelVersionRepresentationOutput):
        self.id = output.id
        self.project_id = output.project_id
        self.name = output.name
        self.status = output.status
        self.description = output.description
        self.technique = output.technique
        self.library = output.library
