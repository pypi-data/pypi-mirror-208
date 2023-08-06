from __future__ import annotations

from typing import TYPE_CHECKING

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json.model_representation import ModelRepresentationOutput
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput

if TYPE_CHECKING:
    from vectice.api.json.model_register import ModelRegisterInput, ModelRegisterOutput

_RETURNS = """
            modelVersion{
                          vecticeId
                          name
                          version
                          description
                          algorithmName
                          framework
                          modelId
                          model {
                            name
                            projectId
                          }
            }
            useExistingModel
            __typename
            """

_RETURNS_MODEL = """
            vecticeId
            createdDate
            updatedDate
            name
            description
            type
            lastVersion {
                vecticeId
                createdDate
                updatedDate
                name
                description
                status
                algorithmName
                framework
                __typename
            }
            project {
                vecticeId
            }
            __typename
"""

_RETURNS_MODEL_VERSION = """
            vecticeId
            createdDate
            updatedDate
            name
            description
            status
            algorithmName
            framework
            model {
                project {
                    vecticeId
                }
            }
            __typename
"""


class GqlModelApi(GqlApi):
    def get_model(self, id: str) -> ModelRepresentationOutput:
        variable_types = "$modelId:VecticeId!"
        kw = "modelId:$modelId"
        variables = {"modelId": id}
        query = GqlApi.build_query(
            gql_query="getModelById",
            variable_types=variable_types,
            returns=_RETURNS_MODEL,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            model_output: ModelRepresentationOutput = Parser().parse_item(response["getModelById"])
            return model_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "model", id)

    def get_model_version(self, id: str) -> ModelVersionRepresentationOutput:
        variable_types = "$modelVersionId:VecticeId!"
        kw = "modelVersionId:$modelVersionId"
        variables = {"modelVersionId": id}
        query = GqlApi.build_query(
            gql_query="getModelVersion",
            variable_types=variable_types,
            returns=_RETURNS_MODEL_VERSION,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            model_output: ModelVersionRepresentationOutput = Parser().parse_item(response["getModelVersion"])
            return model_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "model_version", id)

    def register_model(
        self,
        data: ModelRegisterInput,
        project_id: str,
        phase_id: str | None = None,
        iteration_id: str | None = None,
    ) -> ModelRegisterOutput:
        variables = {"projectId": project_id, "data": data}
        kw = "projectId:$projectId,data:$data"
        variable_types = "$projectId:VecticeId!,$data:ModelRegisterInput!"
        if phase_id:
            variable_types += ",$phaseId:VecticeId!"
            kw += ",phaseId:$phaseId"
            variables["phaseId"] = phase_id
        if iteration_id:
            variable_types += ",$iterationId:VecticeId!"
            kw += ",iterationId:$iterationId"
            variables["iterationId"] = iteration_id
        query_name = "registerModel"
        query = GqlApi.build_query(
            gql_query=query_name,
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            model_output: ModelRegisterOutput = Parser().parse_item(response[query_name])
            return model_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "model", "register model")
