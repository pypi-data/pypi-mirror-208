from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

from gql import gql
from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser
from vectice.utils.api_utils import INDEX_ORDERED, PAGINATE_OUTPUT, get_phase_input
from vectice.utils.vectice_ids_regex import PHASE_VID_REG

if TYPE_CHECKING:
    from vectice.api.json.paged_response import PagedResponse
    from vectice.api.json.phase import PhaseOutput
    from vectice.api.json.step import StepOutput


_RETURNS = """vecticeId
              name
              status
              index
              owner {
                name
              }
              __typename
            """

_RETURNS_LIST = f"""
    {_RETURNS}
    iterationsCount {{
        notStarted
        inProgress
        inReview
        total
    }}
    stepsCount
"""

_RETURNS_PAGE = PAGINATE_OUTPUT.format(_RETURNS_LIST)

_PARENT_FULL = """
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
"""

_RETURNS_FULL = f"""
    {_RETURNS}
    {_PARENT_FULL}
"""

_STEP_DEFINITION_RETURNS = """id
              name
              index
              slug
              description
              __typename
            """


_logger = logging.getLogger(__name__)


class PhaseApi(GqlApi):
    def list_phases(self, parent_id: str) -> PagedResponse[PhaseOutput]:
        gql_query = "getPhaseList"

        variable_types = "$filters:PhaseFiltersInput!,$order:ListOrderInput,$page:PageInput"
        kw = "filters:$filters,order:$order,page:$page"
        variables = {
            "filters": {
                "parentId": parent_id,
            },
            "order": INDEX_ORDERED,
            "page": get_phase_input(),
        }
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS_PAGE, keyword_arguments=kw
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            phase_output: PagedResponse[PhaseOutput] = Parser().parse_paged_response(response[gql_query])
            return phase_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "phase", "list")

    def get_phase(self, phase: str, parent_id: str | None = None, full: bool = False) -> PhaseOutput:
        if re.search(PHASE_VID_REG, phase):
            gql_query = "getPhaseById"
            variable_types = "$id:VecticeId!"
            variables = {"id": phase}
            kw = "id:$id"
        elif parent_id:
            gql_query = "getPhaseByName"
            variable_types = "$name:String!,$parentId:VecticeId!"
            variables = {"name": phase, "parentId": parent_id}
            kw = "name:$name,parentId:$parentId"
        else:
            raise ValueError("Missing parameters: string and parent id required.")
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
            phase_output: PhaseOutput = Parser().parse_item(response[gql_query])
            return phase_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "phase", phase)

    def list_step_definitions(self, parent_id: str) -> list[StepOutput]:
        alias_filter = {"parentId": parent_id, "search": ""}
        returns = f"""items{{
                                    {_STEP_DEFINITION_RETURNS}
                        }}"""
        variable_types = "$filters:BaseDocumentationListFiltersInput!,$order:ListOrderInput"
        kw = "filters:$filters,order:$order"
        variables = {"filters": alias_filter, "order": INDEX_ORDERED}
        query = GqlApi.build_query(
            gql_query="getStepDefinitionList",
            variable_types=variable_types,
            returns=returns,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            iterations_output: list[StepOutput] = Parser().parse_list(response["getStepDefinitionList"]["items"])
            return iterations_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "phase", "list")
