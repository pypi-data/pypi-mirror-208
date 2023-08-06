from __future__ import annotations

import logging
import re
from textwrap import dedent
from typing import TYPE_CHECKING

from rich.table import Table

from vectice.api.http_error_handlers import InvalidReferenceError
from vectice.api.json.phase import PhaseStatus
from vectice.models.iteration import Iteration
from vectice.utils.common_utils import _temp_print
from vectice.utils.last_assets import _get_last_user_and_default_workspace
from vectice.utils.logging_utils import format_description, get_iteration_status
from vectice.utils.vectice_ids_regex import ITERATION_VID_REG

if TYPE_CHECKING:
    from vectice import Connection
    from vectice.api import Client
    from vectice.models import Project, Workspace


_logger = logging.getLogger(__name__)


class Phase:
    """Represent a Vectice phase.

    Phases reflect the real-life phases of the project lifecycle
    (i.e., Business Understanding, Data Preparation, Modeling,
    Deployment, etc.).  The Vectice admin creates the phases of a
    project.

    Phases let you document the goals, assets, and outcomes along with
    the status to organize the project, enforce best practices, allow
    consistency, and capture knowledge.

    Phases contain definitions of steps that are performed
    by data-scientists in order to complete iterations.

    ```tree
    phase 1
        step definition 1
        step definition 2
        step definition 3
    ```

    To get a project's phase:

    ```python
    my_phase = my_project.phase("Business Understanding")
    ```

    Iterations can then be created for this phase,
    to complete the phase steps:

    ```python
    my_origin_dataset = ...
    my_iteration = my_phase.create_iteration()
    my_iteration.step_origin_dataset = my_origin_dataset
    ```

    NOTE: **Phases and Steps Definitions are created in the Vectice App,
    Iterations are created from the Vectice Python API.**

    See the documentation of [Iterations][vectice.models.Iteration]
    for more information about iterations.
    """

    __slots__ = [
        "_id",
        "_project",
        "_name",
        "_index",
        "_status",
        "_client",
        "_current_iteration",
        "_pointers",
    ]

    def __init__(
        self,
        id: str,
        project: Project,
        name: str,
        index: int,
        status: PhaseStatus = PhaseStatus.NotStarted,
    ):
        """Initialize a phase.

        Vectice users shouldn't need to instantiate Phases manually,
        but here are the phase parameters.

        Parameters:
            id: The phase identifier.
            project: The project to which the phase belongs.
            name: The name of the phase.
            index: The index of the phase.
            status: The status of the phase.
        """
        self._id = id
        self._project = project
        self._name = name
        self._index = index
        self._status = status
        self._client: Client = self._project._client
        self._current_iteration: Iteration | None = None

    def __repr__(self):
        return f"Phase (name='{self.name}', id={self.id}, status='{self.status.name}')"

    def __eq__(self, other: object):
        if not isinstance(other, Phase):
            return NotImplemented
        return self.id == other.id

    @property
    def id(self) -> str:
        """The phase's id.

        Returns:
            The phase's id.
        """
        return self._id

    @id.setter
    def id(self, phase_id: str):
        """Set the phase's id.

        Parameters:
            phase_id: The phase id to set.
        """
        self._id = phase_id

    @property
    def name(self) -> str:
        """The phase's name.

        Returns:
            The phase's name.
        """
        return self._name

    @property
    def index(self) -> int:
        """The phase's index.

        Returns:
            The phase's index.
        """
        return self._index

    @property
    def status(self) -> PhaseStatus:
        """The phase's status.

        Returns:
            The phase's status.
        """
        return self._status

    @property
    def properties(self) -> dict:
        """The phase's name, id, and index.

        Returns:
            A dictionary containing the `name`, `id`, and `index` items.
        """
        return {"name": self.name, "id": self.id, "index": self.index}

    @property
    def iterations(self) -> list[Iteration]:
        """The phase's iterations.

        Returns:
            The phase's iterations.
        """
        iteration_outputs = self._client.list_iterations(self.id)
        return [Iteration(item.id, item.index, self, item.status) for item in iteration_outputs.list]

    def list_iterations(self, only_mine: bool = False) -> None:
        """Prints a list of iterations belonging to the phase in a tabular format, limited to the last 10 items.

        Parameters:
            only_mine (boolean, default 'False'): Display only the iterations where the user is the owner
        Returns:
            None

        """
        iteration_outputs = self._client.list_iterations(self.id, only_mine)
        rich_table = Table(expand=True, show_edge=False)

        rich_table.add_column("Id", justify="left", no_wrap=True, min_width=3, max_width=20)
        rich_table.add_column("Index", justify="left", no_wrap=True, min_width=5, max_width=10)
        rich_table.add_column("Status", justify="left", no_wrap=True, min_width=3, max_width=15)
        rich_table.add_column("Owner", justify="left", no_wrap=True, min_width=5, max_width=15)

        for iteration in iteration_outputs.list:
            rich_table.add_row(
                str(iteration.id),
                str(iteration.index),
                get_iteration_status(iteration.status, iteration.starred),
                iteration.ownername,
            )
        description = f"""There are {iteration_outputs.total} iterations in the phase {self.name!r} and a maximum of 10 iterations are displayed in the table below:"""
        link = dedent(
            f"""
        # For quick access to the list of iterations in the Vectice web app, visit:
        # {self._client.auth._API_BASE_URL}/phase/{self.id}/iterations?w={self.workspace.id}"""
        ).lstrip()
        _temp_print(description)
        _temp_print(table=rich_table)
        _temp_print(link)

    def list_steps(self) -> None:
        """Prints a list of step definitions belonging to the phase in a tabular format, limited to the first 10 items. A link is provided to view the remaining step definitions.

        Returns:
            None
        """
        steps_output = self._client.list_step_definitions(self.id)
        user_name, _ = _get_last_user_and_default_workspace(self._client)

        rich_table = Table(expand=True, show_edge=False)

        rich_table.add_column("shortcut", justify="left", no_wrap=True, min_width=3, max_width=20)
        rich_table.add_column("name", justify="left", no_wrap=True, min_width=5, max_width=10)
        rich_table.add_column("description", justify="left", no_wrap=True, min_width=3, max_width=15)

        for count, step in enumerate(steps_output, 1):
            if count > 10:
                break
            rich_table.add_row(step.slug, step.name, format_description(step.description))
        description = f"""There are {len(steps_output)} steps required in the phase {self.name!r} and a maximum of 10 steps are displayed in the table below:"""
        link = dedent(
            f"""
        For quick access to the list of step definitions in the Vectice web app, visit:
        {self._client.auth._API_BASE_URL}/phase/{self.id}/steps?w={self.workspace.id}"""
        ).lstrip()
        _temp_print(description)
        _temp_print(table=rich_table)
        _temp_print(link)

    def iteration(self, index: int | str) -> Iteration:
        """Get an iteration.

        Fetch and return an iteration by index.

        Parameters:
            index: The id of an existing iteration.

        Returns:
            An iteration.
        """
        if isinstance(index, str):
            if re.search(ITERATION_VID_REG, index):
                iteration_output = self._client.get_iteration(index)
            else:
                raise InvalidReferenceError("iteration", index)
        else:
            iteration_output = self._client.get_iteration_by_index(self.id, index)

        iteration_object = Iteration(
            id=iteration_output.id,
            index=iteration_output.index,
            phase=self,
            status=iteration_output.status,
        )
        logging_output = dedent(
            f"""
                Iteration number '{iteration_output.index!r}' successfully retrieved."

                For quick access to the Iteration in the Vectice web app, visit:
                {self._client.auth._API_BASE_URL}/browse/iteration/{iteration_object.id}"""
        ).lstrip()
        _logger.info(logging_output)
        self._current_iteration = iteration_object
        return iteration_object

    def create_iteration(self) -> Iteration:
        """Create a new iteration.

        Create and return an iteration.

        Returns:
            An iteration.
        """
        iteration_output = self._client.create_iteration(self.id)
        logging_output = dedent(
            f"""
        New Iteration number '{iteration_output.index!r}' created.

        For quick access to the Iteration in the Vectice web app, visit:
        {self._client.auth._API_BASE_URL}/browse/iteration/{iteration_output.id}"""
        ).lstrip()
        _logger.info(logging_output)

        iteration_object = Iteration(
            id=iteration_output.id,
            index=iteration_output.index,
            phase=self,
            status=iteration_output.status,
        )
        self._current_iteration = iteration_object
        return iteration_object

    @property
    def connection(self) -> Connection:
        """The connection to which this phase belongs.

        Returns:
            The connection to which this phase belongs.
        """
        return self._project.connection

    @property
    def workspace(self) -> Workspace:
        """The workspace to which this phase belongs.

        Returns:
            The workspace to which this phase belongs.
        """
        return self._project.workspace

    @property
    def project(self) -> Project:
        """The project to which this phase belongs.

        Returns:
            The project to which this phase belongs.
        """
        return self._project
