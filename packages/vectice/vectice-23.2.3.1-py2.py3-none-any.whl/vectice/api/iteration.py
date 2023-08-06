from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.api.json.paged_response import PagedResponse
from vectice.utils.api_utils import INDEX_ORDERED_DESC, PAGINATE_OUTPUT, get_phase_input

if TYPE_CHECKING:
    from vectice.api.json.iteration import IterationInput, IterationOutput

_logger = logging.getLogger(__name__)

_RETURNS_LIST = """vecticeId
            index
            status
            owner {
                id
                name
            }
            starred
            __typename
            """

_RETURNS_PAGE = PAGINATE_OUTPUT.format(_RETURNS_LIST)

_BASE_RETURNS = """vecticeId
            index
            status
            owner {
                    id
                    name
                    }
            starred
            steps {
                    slug
                    id
                    name
                    stepType
                    artifacts {
                        type
                        datasetVersion {
                            vecticeId
                        }
                        modelVersion {
                            vecticeId
                        }
                        entityFileId
                        text
                        type
                    }
            }
            __typename
            """
_BASE_PARENT = """
            phase {
                    vecticeId
                    name
                    status
                    index
                    __typename
              }
"""

_RETURNS = f"""
    {_BASE_RETURNS}
    {_BASE_PARENT}
"""

_PARENT_FULL = """
            phase {
                    vecticeId
                    name
                    status
                    index
                    __typename
                    parent {
                        vecticeId
                        name
                        description
                        workspace {
                            vecticeId
                            name
                            description
                            __typename
                        }
                        __typename
                    }
              }
"""

_RETURNS_FULL = f"""
    {_BASE_RETURNS}
    {_PARENT_FULL}
"""

_RETURNS_LAST_ASSETS = """vecticeId
            index
            status
            phase {
                    vecticeId
                    name
                    status
                    __typename
                    parent {
                            vecticeId
                            name
                            __typename
                            workspace{
                                    vecticeId
                                    name
                                    __typename
                            }
                    }
              }
              steps{
                    slug
                    id
                    name
                    index
                    completed
                    updatedDate
                    __typename
              }
            __typename
            """


class IterationApi(GqlApi):
    def list_iterations(self, parent_id: str, only_mine: bool = False) -> PagedResponse[IterationOutput]:
        gql_query = "getIterationList"
        alias_filter = {"phaseId": parent_id, "onlyMine": only_mine}
        variable_types = "$filters:IterationFiltersInput!,$order:ListOrderInput,$page:PageInput"
        kw = "filters:$filters,order:$order,page:$page"
        variables = {
            "filters": alias_filter,
            "order": INDEX_ORDERED_DESC,
            "page": get_phase_input(),
        }
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_PAGE,
            keyword_arguments=kw,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iterations_output: PagedResponse[IterationOutput] = Parser().parse_paged_response(response[gql_query])
            return iterations_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", "list")

    def create_iteration(self, phase_id: str) -> IterationOutput:
        gql_query = "createIteration"
        variable_types = "$phaseId:VecticeId!"
        variables = {"phaseId": phase_id}
        kw = "phaseId:$phaseId"
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS, keyword_arguments=kw, query=False
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iteration_output: IterationOutput = Parser().parse_item(response[gql_query])
            return iteration_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", phase_id)

    def get_iteration(self, iteration_id: str, full: bool = False) -> IterationOutput:
        gql_query = "getIterationById"
        variable_types = "$id:VecticeId!"
        variables = {"id": iteration_id}
        kw = "id:$id"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_FULL if full else _RETURNS,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iteration_output: IterationOutput = Parser().parse_item(response[gql_query])
            return iteration_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)

    def get_iteration_last_assets(self, iteration_id: int) -> IterationOutput:
        gql_query = "getIterationById"
        variable_types = "$id:VecticeId!"
        variables = {"id": iteration_id}
        kw = "id:$id"
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=_RETURNS_LAST_ASSETS,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iteration_output: IterationOutput = Parser().parse_item(response[gql_query])
            return iteration_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)

    def get_iteration_by_index(self, phase_id: str, index: int) -> IterationOutput:
        gql_query = "getIterationByIndex"
        variable_types = "$index:Float!,$phaseId:VecticeId!"
        variables = {"index": index, "phaseId": phase_id}
        kw = "index:$index,phaseId:$phaseId"
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS, keyword_arguments=kw, query=True
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iteration_output: IterationOutput = Parser().parse_item(response[gql_query])
            return iteration_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration_index", index)

    def update_iteration(self, iteration: IterationInput, iteration_id: str) -> IterationOutput:
        variable_types = "$id:VecticeId!,$data:IterationUpdateInput!"
        kw = "id:$id,data:$data"
        variables = {"id": iteration_id, "data": iteration}
        query = GqlApi.build_query(
            gql_query="updateIteration",
            variable_types=variable_types,
            returns=_RETURNS,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iteration_output: IterationOutput = Parser().parse_item(response["updateIteration"])
            return iteration_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", "put")

    def delete_iteration(self, iteration_id: str) -> None:
        variable_types = "$id:VecticeId!"
        kw = "id:$id"
        variables = {"id": iteration_id}
        query = GqlApi.build_query(
            gql_query="removeIteration",
            variable_types=variable_types,
            keyword_arguments=kw,
            query=False,
        )
        query_built = gql(query)
        try:
            self.execute(query_built, variables)
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "iteration", iteration_id)
