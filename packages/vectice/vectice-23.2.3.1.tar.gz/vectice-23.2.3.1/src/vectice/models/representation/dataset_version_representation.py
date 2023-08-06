from vectice.api.json.dataset_version_representation import DatasetVersionRepresentationOutput


class DatasetVersionRepresentation:
    def __init__(self, output: DatasetVersionRepresentationOutput):
        self.id = output.id
        self.project_id = output.project_id
        self.name = output.name
        self.description = output.description
