from vectice.api.json.dataset_representation import DatasetRepresentationOutput
from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation


class DatasetRepresentation:
    def __init__(self, output: DatasetRepresentationOutput):
        self.id = output.id
        self.project_id = output.project_id
        self.name = output.name
        self.type = output.type
        self.origin = output.origin
        self.description = output.description
        self.version = DatasetVersionRepresentation(output.version)
