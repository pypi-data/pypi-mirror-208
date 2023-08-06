from __future__ import annotations

import re
from typing import TYPE_CHECKING

from gql import gql

from vectice.utils.vectice_ids_regex import WORKSPACE_VID_REG

if TYPE_CHECKING:
    from vectice.api.json import WorkspaceOutput

from gql.transport.exceptions import TransportQueryError

from vectice.api.gql_api import GqlApi, Parser

_RETURNS = """
            name
            description
            vecticeId
            __typename
"""


class WorkspaceApi(GqlApi):
    def get_workspace(self, workspace: str) -> WorkspaceOutput:
        search_vectice_id = re.search(WORKSPACE_VID_REG, workspace)
        if search_vectice_id:
            gql_query = "getWorkspaceById"
            variable_types = "$workspaceId:VecticeId!"
            variables = {"workspaceId": workspace}
            kw = "workspaceId:$workspaceId"
        else:
            gql_query = "getWorkspaceByName"
            variable_types = "$name:String!"
            variables = {"name": workspace}
            kw = "name:$name"
        query = GqlApi.build_query(
            gql_query=gql_query, variable_types=variable_types, returns=_RETURNS, keyword_arguments=kw, query=True
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            workspace_output: WorkspaceOutput = Parser().parse_item(response[gql_query])
            return workspace_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "workspace", workspace)

    def list_workspaces(self, search: str | None, page_index: int, page_size: int) -> list[WorkspaceOutput]:
        gql_query = "getUserWorkspaceList"
        page = {
            "index": page_index,
            "size": page_size,
        }
        filters = {
            "searchFilter": {"search": search if search is not None else "", "fields": "name"},
        }
        variable_types = "$page: PageInput!,$filters:WorkspaceListFiltersInput!"
        variables = {"page": page, "filters": filters}
        kw = "page:$page,filters:$filters"
        returns = f"""items{{
                    {_RETURNS}
        }}"""
        query = GqlApi.build_query(
            gql_query=gql_query,
            variable_types=variable_types,
            returns=returns,
            keyword_arguments=kw,
            query=True,
        )
        query_built = gql(query)
        try:
            response = self.execute(query_built, variables)
            workspace_output: list[WorkspaceOutput] = Parser().parse(response["getUserWorkspaceList"]["items"])  # type: ignore[assignment]
            return workspace_output
        except TransportQueryError as e:
            self._error_handler.handle_post_gql_error(e, "workspaces", "list")
