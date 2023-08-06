from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json.dataset_representation import DatasetRepresentationOutput
from vectice.api.json.dataset_version_representation import DatasetVersionRepresentationOutput

if TYPE_CHECKING:
    from vectice.api.json.dataset_register import DatasetRegisterInput, DatasetRegisterOutput


_logger = logging.getLogger(__name__)

# TODO JobRun for lineages
_RETURNS = """
            datasetVersion {
                          vecticeId
                          name
                          dataSet {
                            name
                            projectId
                          }
            }
            useExistingDataset
            useExistingVersion
            __typename
            """

_RETURNS_DATASET = """
            vecticeId
            createdDate
            updatedDate
            name
            description
            type
            sourceOrigin
            lastVersion {
                vecticeId
                createdDate
                updatedDate
                name
                description
                __typename
            }
            project {
                vecticeId
            }
            __typename
"""

_RETURNS_DATASET_VERSION = """
            vecticeId
            createdDate
            updatedDate
            name
            description
            dataSet {
                project {
                    vecticeId
                }
            }
            __typename
"""


class GqlDatasetApi(GqlApi):
    def get_dataset(self, id: str) -> DatasetRepresentationOutput:
        variable_types = "$datasetId:VecticeId!"
        kw = "datasetId:$datasetId"
        variables = {"datasetId": id}
        query = GqlApi.build_query(
            gql_query="getDataset",
            variable_types=variable_types,
            returns=_RETURNS_DATASET,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            dataset_output: DatasetRepresentationOutput = Parser().parse_item(response["getDataset"])
            return dataset_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset", id)

    def get_dataset_version(self, id: str) -> DatasetVersionRepresentationOutput:
        variable_types = "$datasetVersionId:VecticeId!"
        kw = "datasetVersionId:$datasetVersionId"
        variables = {"datasetVersionId": id}
        query = GqlApi.build_query(
            gql_query="getDatasetVersion",
            variable_types=variable_types,
            returns=_RETURNS_DATASET_VERSION,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            dataset_output: DatasetVersionRepresentationOutput = Parser().parse_item(response["getDatasetVersion"])
            return dataset_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset_version", id)

    def register_dataset(
        self,
        data: DatasetRegisterInput,
        project_id: str | None = None,
        phase_id: str | None = None,
        iteration_id: str | None = None,
    ) -> DatasetRegisterOutput:
        if phase_id and project_id and not iteration_id:
            variable_types = "$projectId:VecticeId!,$phaseId:VecticeId!,$data:DatasetRegisterInput!"
            kw = "projectId:$projectId,phaseId:$phaseId,data:$data"
            variables = {"projectId": project_id, "phaseId": phase_id, "data": data}
        elif project_id and phase_id and iteration_id:
            variable_types = (
                "$projectId:VecticeId!,$phaseId:VecticeId!,$iterationId:VecticeId!,$data:DatasetRegisterInput!"
            )
            kw = "projectId:$projectId,phaseId:$phaseId,iterationId:$iterationId,data:$data"
            variables = {"projectId": project_id, "phaseId": phase_id, "iterationId": iteration_id, "data": data}
        elif project_id:
            variable_types = "$projectId:VecticeId!,$data:DatasetRegisterInput!"
            kw = "projectId:$projectId,data:$data"
            variables = {"projectId": project_id, "data": data}
        else:
            raise RuntimeError("The provided parent child ids do not match.")

        query = GqlApi.build_query(
            gql_query="registerDataset",
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            dataset_output: DatasetRegisterOutput = Parser().parse_item(response["registerDataset"])
            return dataset_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "dataset", "register dataset")
