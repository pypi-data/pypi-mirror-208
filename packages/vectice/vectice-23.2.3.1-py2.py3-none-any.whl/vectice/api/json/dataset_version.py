class DatasetOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def project_id(self) -> int:
        return int(self["projectId"])


class DatasetVersionOutput(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "dataSet" in self:
            self._dataset: DatasetOutput = DatasetOutput(**self["dataSet"])
        else:
            self._dataset = None

    @property
    def id(self) -> str:
        return str(self["vecticeId"])

    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def dataset(self) -> DatasetOutput:
        return self._dataset
