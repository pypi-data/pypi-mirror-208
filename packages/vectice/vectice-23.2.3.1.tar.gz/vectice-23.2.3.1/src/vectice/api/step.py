from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from gql import gql

from vectice.utils.api_utils import INDEX_ORDERED

if TYPE_CHECKING:
    from vectice.api.json import IterationStepArtifactInput, StepOutput

from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json.step import StepType

_logger = logging.getLogger(__name__)

_RETURNS_WITH_STEPS = """
                items {
                    id
                    index
                    name
                    completed
                    description
                    stepType
                    slug
                    artifacts {
                                entityFileId
                                modelVersion {
                                    vecticeId
                                }
                                datasetVersion {
                                    vecticeId
                                }
                                text
                                type
                    }
                    __typename
                }
            """

_RETURNS = """
                id
                index
                name
                completed
                description
                stepType
                slug
                artifacts {
                                entityFileId
                                modelVersion {
                                    vecticeId
                                }
                                datasetVersion {
                                    vecticeId
                                }
                                text
                                type
                    }
                __typename
            """


class StepApi(GqlApi):
    def list_steps(self, iteration_id: str) -> list[StepOutput]:
        gql_query = "getIterationStepList"
        variable_types = "$parentId:VecticeId!,$order:ListOrderInput"
        variables = {"parentId": iteration_id, "order": INDEX_ORDERED}
        kw = "parentId:$parentId,order:$order"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_WITH_STEPS,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            step_output: list[StepOutput] = Parser().parse_list(response[gql_query]["items"])
            return step_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)

    def add_iteration_step_artifact(self, data: IterationStepArtifactInput, step_id: int) -> StepOutput:
        gql_query = "addIterationStepArtifact"
        variable_types = "$id:Float!,$data:IterationStepArtifactInput!"
        variables = {"id": step_id, "data": data}
        kw = "id:$id, data:$data"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            step_output: StepOutput = Parser().parse_item(response[gql_query])
            return step_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "step", step_id)

    def update_iteration_step_artifact(
        self,
        step_id: int,
        step_type: StepType,
        artifacts: list[IterationStepArtifactInput] | None = None,
    ) -> StepOutput:
        gql_query = "updateIterationStepContent"
        variable_types = "$id:Float!,$data:IterationStepUpdateInput!"
        variables: dict = {
            "id": step_id,
            "data": {
                "stepType": step_type.value,
            },
        }
        if artifacts:
            variables["data"]["artifacts"] = artifacts
        kw = "id:$id, data:$data"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            step_output: StepOutput = Parser().parse_item(response[gql_query])
            return step_output
        except TransportQueryError as e:
            print(e)
            self._error_handler.handle_post_gql_error(e, "step", step_id)

    def get_step(self, step: str, iteration_id: str) -> StepOutput:
        if isinstance(step, str) and iteration_id:
            gql_query = "getStepByName"
            variable_types = "$name:String!,$parentId:VecticeId!"
            variables = {"name": step, "parentId": iteration_id}
            kw = "name:$name,parentId:$parentId"
        else:
            raise ValueError("Missing parameters: string and parent id required.")
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS, keyword_arguments=kw, query=True
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            step_output: StepOutput = Parser().parse_item(response[gql_query])
            return step_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "step", step)
