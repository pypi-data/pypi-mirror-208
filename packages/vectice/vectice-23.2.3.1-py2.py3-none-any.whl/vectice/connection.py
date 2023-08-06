from __future__ import annotations

import logging
import os
import re
from contextlib import suppress
from pathlib import Path
from textwrap import dedent

import dotenv
from rich.table import Table

from vectice.api import Client
from vectice.api.http_error_handlers import InvalidIdError
from vectice.api.json.iteration import IterationOutput
from vectice.api.json.last_assets import ActivityTargetType
from vectice.api.json.phase import PhaseOutput
from vectice.api.json.project import ProjectOutput
from vectice.api.json.workspace import WorkspaceOutput
from vectice.models.iteration import Iteration
from vectice.models.phase import Phase
from vectice.models.project import Project
from vectice.models.representation.dataset_representation import DatasetRepresentation
from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
from vectice.models.representation.model_representation import ModelRepresentation
from vectice.models.representation.model_version_representation import ModelVersionRepresentation
from vectice.models.workspace import Workspace
from vectice.utils.common_utils import _temp_print, hide_logs
from vectice.utils.configuration import Configuration
from vectice.utils.last_assets import _connection_logging, _get_last_assets, _get_last_user_and_default_workspace
from vectice.utils.logging_utils import CONNECTION_PROJECT_LOGGING, CONNECTION_WORKSPACE_LOGGING, format_description
from vectice.utils.vectice_ids_regex import (
    DATASET_VERSION_VID_REG,
    DATASET_VID_REG,
    ITERATION_VID_REG,
    MODEL_VERSION_VID_REG,
    MODEL_VID_REG,
    PHASE_VID_REG,
    PROJECT_VID_REG,
    WORKSPACE_VID_REG,
)

_logger = logging.getLogger(__name__)
DEFAULT_API_ENDPOINT = "https://app.vectice.com"
CAN_NOT_BE_EMPTY_ERROR_MESSAGE = "%s can not be empty."


class Connection:
    """Connect to the Vectice backend (application).

    The Connection class encapsulates a connection to the Vectice App.
    Thus, it authenticates and connects to Vectice.
    This allows you to start interacting with your Vectice assets.

    A Connection can be initialized in three ways:

    1. Passing the relevant arguments to authenticate and connect to Vectice:

        ```python
        import vectice

        connection = vectice.connect(
            api_token="API_TOKEN_FROM_VECTICE",
            host="https://app.vectice.com",
        )
        ```

    2. Passing the path to a configuration file:

        ```python
        import vectice

        connection = vectice.connect(config="vectice_config.json")
        ```

    3. Letting Vectice find the configuration file in specific locations:

        ```python
        import vectice

        connection = vectice.connect()
        ```

    See [`Connection.connect`][vectice.connection.Connection.connect] for more info.
    """

    USER_FILES_PATH = [
        ".vectice",
        str(Path.home() / ".vectice"),
        ".env",
        str(Path.home() / ".env"),
        "/etc/vectice/api.cfg",
    ]

    def __init__(
        self,
        api_token: str,
        host: str,
        workspace: str | None = None,
        project: str | None = None,
    ):
        """Initialize a connection.

        Parameters:
            api_token: Your private api token.
            host: The address of the Vectice application.
            workspace: The workspace you want to work in.
            project: The project you want to work in.

        Raises:
            RuntimeError: When the API and backend versions are incompatible.
        """
        logging.getLogger("Client").propagate = True
        self._client = Client(
            workspace=workspace,
            project=project,
            token=api_token,
            api_endpoint=host,
            auto_connect=True,
            allow_self_certificate=True,
        )
        compatibility = self._client.check_compatibility()
        if compatibility.status != "OK":
            if compatibility.status == "Error":
                _logger.error(f"compatibility error: {compatibility.message}")
                raise RuntimeError(f"compatibility error: {compatibility.message}")
            else:
                _logger.warning(f"compatibility warning: {compatibility.message}")

    def __repr__(self) -> str:
        return (
            "Connection("
            + f"workspace={self._client.workspace.name if self._client.workspace else 'None'}, "
            + f"host={self._client.auth.api_base_url}, "
        )

    @property
    def version_api(self) -> str:
        return self._client.version_api

    @property
    def version_backend(self) -> str:
        return self._client.version_backend

    def workspace(self, workspace: str) -> Workspace:
        """Get a workspace.

        Parameters:
            workspace: The id or the name of the desired workspace.

        Returns:
            The desired workspace.
        """
        output = self._client.get_workspace(workspace)
        result = Workspace(output.id, output.name, output.description)
        result.__post_init__(self._client, self)
        logging_output = dedent(
            f"""
                        Workspace {result.name!r} successfully retrieved."

                        For quick access to the workspace in the Vectice web app, visit:
                        {self._client.auth._API_BASE_URL}/browse/workspace/{result.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return result

    def _build_workspace_from_output(self, output: WorkspaceOutput) -> Workspace:
        workspace = Workspace(output.id, output.name, output.description)
        workspace.__post_init__(self._client, self)
        return workspace

    def _build_project_from_output(self, output: ProjectOutput) -> Project:
        workspace = self._build_workspace_from_output(output.workspace)
        project = Project(output.id, workspace, output.name, output.description)
        return project

    def _build_phase_from_output(self, output: PhaseOutput) -> Phase:
        if output.project is None:
            raise RuntimeError("Failed to get back project from phase output")
        project = self._build_project_from_output(output.project)
        phase = Phase(output.id, project, output.name, output.index, output.status)
        return phase

    def _build_iteration_from_output(self, output: IterationOutput) -> Iteration:
        if output.phase is None:
            raise RuntimeError("Failed to get back phase from iteration output")
        phase = self._build_phase_from_output(output.phase)
        iteration = Iteration(output.id, output.index, phase, output.status)
        return iteration

    def browse(
        self, asset: str
    ) -> (
        Workspace
        | Project
        | Phase
        | Iteration
        | DatasetRepresentation
        | ModelRepresentation
        | DatasetVersionRepresentation
        | ModelVersionRepresentation
    ):
        """Get an asset.

        Parameters:
            asset: The id of the desired asset.

        Returns:
            The desired asset.
        """
        if re.search(WORKSPACE_VID_REG, asset):
            return self.workspace(asset)
        elif re.search(PROJECT_VID_REG, asset):
            return self.project(asset)
        elif re.search(PHASE_VID_REG, asset):
            return self.phase(asset)
        elif re.search(ITERATION_VID_REG, asset):
            return self.iteration(asset)
        elif re.search(MODEL_VID_REG, asset):
            return self.model(asset)
        elif re.search(MODEL_VERSION_VID_REG, asset):
            return self.model_version(asset)
        elif re.search(DATASET_VID_REG, asset):
            return self.dataset(asset)
        elif re.search(DATASET_VERSION_VID_REG, asset):
            return self.dataset_version(asset)

        raise InvalidIdError("asset", asset)

    def project(self, project: str) -> Project:
        """Get a project.

        Parameters:
            project: The id of the desired project.

        Returns:
            The desired project.
        """
        if not re.search(PROJECT_VID_REG, project):
            raise InvalidIdError("project", project)
        output = self._client.get_project(project)
        logging_output = dedent(
            f"""
                Project {output.name!r} successfully retrieved."

                For quick access to the Project in the Vectice web app, visit:
                {self._client.auth._API_BASE_URL}/browse/project/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return self._build_project_from_output(output)

    def phase(self, phase: str) -> Phase:
        """Get a phase.

        Parameters:
            phase: The id of the desired phase.

        Returns:
            The desired phase.
        """
        if not re.search(PHASE_VID_REG, phase):
            raise InvalidIdError("phase", phase)
        output = self._client.get_full_phase(phase)

        logging_output = dedent(
            f"""
                        Phase {output.name!r} successfully retrieved."

                        For quick access to the Phase in the Vectice web app, visit:
                        {self._client.auth._API_BASE_URL}/browse/phase/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return self._build_phase_from_output(output)

    def iteration(self, iteration: str) -> Iteration:
        """Get an iteration.

        Parameters:
            iteration: The id of the desired iteration.

        Returns:
            The desired iteration.
        """
        if not re.search(ITERATION_VID_REG, iteration):
            raise InvalidIdError("iteration", iteration)
        output = self._client.get_full_iteration(iteration)
        logging_output = dedent(
            f"""
                Iteration number {output.index!r} successfully retrieved."

                For quick access to the Iteration in the Vectice web app, visit:
                {self._client.auth._API_BASE_URL}/browse/iteration/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return self._build_iteration_from_output(output)

    def dataset(self, dataset: str) -> DatasetRepresentation:
        """Get a dataset.

        Parameters:
            dataset: The id of the desired dataset.

        Returns:
            The representation of the desired dataset.
        """
        if not re.search(DATASET_VID_REG, dataset):
            raise InvalidIdError("dataset", dataset)
        output = self._client.get_dataset(dataset)
        logging_output = dedent(
            f"""
                Dataset {output.name!r} successfully retrieved."

                For quick access to the Dataset in the Vectice web app, visit:
                {self._client.auth._API_BASE_URL}/browse/dataset/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return DatasetRepresentation(output)

    def dataset_version(self, version: str) -> DatasetVersionRepresentation:
        """Get a dataset version.

        Parameters:
            version: The id of the desired dataset version.

        Returns:
            The representation of the desired dataset version.
        """
        if not re.search(DATASET_VERSION_VID_REG, version):
            raise InvalidIdError("dataset_version", version)
        output = self._client.get_dataset_version(version)
        logging_output = dedent(
            f"""
                Dataset version {output.name!r} successfully retrieved."

                For quick access to the Dataset version in the Vectice web app, visit:
                {self._client.auth._API_BASE_URL}/browse/datasetversion/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return DatasetVersionRepresentation(output)

    def model(self, model: str) -> ModelRepresentation:
        """Get a model.

        Parameters:
            model: The id of the desired model.

        Returns:
            The representation of the desired model.
        """
        if not re.search(MODEL_VID_REG, model):
            raise InvalidIdError("model", model)
        output = self._client.get_model(model)
        logging_output = dedent(
            f"""
                Model {output.name!r} successfully retrieved."

                For quick access to the Model in the Vectice web app, visit:
                {self._client.auth._API_BASE_URL}/browse/model/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return ModelRepresentation(output)

    def model_version(self, version: str) -> ModelVersionRepresentation:
        """Get a model version.

        Parameters:
            version: The id of the desired model version.

        Returns:
            The representation of the desired model version.
        """
        if not re.search(MODEL_VERSION_VID_REG, version):
            raise InvalidIdError("model_version", version)
        output = self._client.get_model_version(version)
        logging_output = dedent(
            f"""
                Model version {output.name!r} successfully retrieved."

                For quick access to the Model version in the Vectice web app, visit:
                {self._client.auth._API_BASE_URL}/browse/modelversion/{output.id}"""
        ).lstrip()
        _logger.info(logging_output)
        return ModelVersionRepresentation(output)

    def list_workspaces(self) -> None:
        """Prints a list of workspaces in a tabular format, limited to the first 10 items. A link is provided to view the remaining workspaces.

        Returns:
            None
        """
        workspace_outputs = self._client.list_workspaces()
        user_name, _ = _get_last_user_and_default_workspace(self._client)

        rich_table = Table(expand=True, show_edge=False)

        rich_table.add_column("workspace id", justify="left", no_wrap=True, min_width=4, max_width=10)
        rich_table.add_column("name", justify="left", no_wrap=True, max_width=20)
        rich_table.add_column("description", justify="left", no_wrap=True, max_width=50)

        for count, workspace in enumerate(workspace_outputs, 1):
            if count > 10:
                break
            rich_table.add_row(str(workspace.id), workspace.name, format_description(workspace.description))

        description = dedent(
            f"""
        There are {len(workspace_outputs)} workspaces and a maximum of 10 workspaces are displayed in the table below:"""
        ).lstrip()
        tips = dedent(
            """
        To access your personal workspace, use \033[1mconnection\033[0m.my_workspace
        To access a specific workspace, use \033[1mconnection\033[0m.workspace(Workspace ID)"""
        ).lstrip()
        link = dedent(
            f"""
        For quick access to the list of workspaces in the Vectice web app, visit:
        {self._client.auth._API_BASE_URL}/workspaces"""
        ).lstrip()
        _temp_print(description)
        _temp_print(table=rich_table)
        _temp_print(tips)
        _temp_print(link)

    @property
    def workspaces(self) -> list[Workspace] | None:
        """List the workspaces to which this connection has access.

        Returns:
            The workspaces to which this connection has access.
        """
        _, default_workspace_id = _get_last_user_and_default_workspace(self._client)
        outputs = self._client.list_workspaces()
        results: list[Workspace] = []
        for output in outputs:
            workspace = Workspace(id=output.id, name=output.name, description=output.description)
            workspace.__post_init__(self._client, self)
            if output.id == default_workspace_id:
                results.insert(0, workspace)
                continue
            results.append(workspace)
        return results

    @property
    def my_workspace(self) -> Workspace:
        """Retrieve your personal workspace.

        Returns:
            Personal workspace.
        """
        asset = self._client.get_user_and_default_workspace()
        if not asset.get("defaultWorkspace"):
            raise ValueError("Default workspace is not set.")
        return self.workspace(asset["defaultWorkspace"]["vecticeId"])

    @property
    def last_workspace(self) -> Workspace:
        """Retrieve last workspace with activity.

        Returns:
            Last workspace with activity.
        """
        target_types = [activity for activity in ActivityTargetType]
        asset = _get_last_assets(target_types, self._client, _logger)
        if not asset or not asset.get("workspace"):
            raise ValueError("Workspace with activity not found.")
        return self.workspace(asset["workspace"]["vecticeId"])

    @staticmethod
    def connect(
        api_token: str | None = None,
        host: str | None = None,
        config: str | None = None,
        workspace: str | None = None,
        project: str | None = None,
    ) -> Connection | Workspace | Project | None:
        """Method to connect to the Vectice backend (application).

        Authentication credentials are retrieved, in order, from:

        1. keyword arguments
        2. configuration file (`config` parameter)
        3. environment variables
        4. environment files in the following order
            - `.vectice` of the working directory
            - `.vectice` of the user home directory
            - `.env` of the working directory
            - `.env` of the user home directory
            - `/etc/vectice/api.cfg` file

        This method uses the `api_token`, `host`, `workspace`, `project` arguments
        or the JSON config provided. The JSON config file is available from the Vectice
        webapp when creating an API token.

        Parameters:
            api_token: The api token provided by the Vectice webapp.
            host: The backend host to which the client will connect.
                If not found, the default endpoint https://app.vectice.com is used.
            config: A JSON config file containing keys VECTICE_API_TOKEN and
                VECTICE_API_ENDPOINT as well as optionally WORKSPACE and PROJECT.
            workspace: The name or id of an optional workspace to return.
            project: The name or id of an optional project to return.

        Raises:
            ValueError: When a project is specified without a workspace.

        Returns:
            A Connection, Workspace, or Project.
        """
        host = host or Connection._get_host(config)
        api_token = api_token or Connection._get_api_token(host, config)
        workspace = workspace or Connection._get_workspace(config)
        project = project or Connection._get_project(config)
        connection = Connection(api_token=api_token, host=host, workspace=workspace, project=project)
        user_name, workspace_id = _get_last_user_and_default_workspace(connection._client)
        url = connection._client.auth.api_base_url
        if workspace and not project:
            return connection.get_workspace(workspace, user_name, url)
        if workspace and project:
            return connection.get_project(workspace, project, user_name, url)
        _connection_logging(_logger, user_name, url, workspace_id)
        return connection

    @staticmethod
    def _get_host(config: str | None) -> str:
        try:
            return Connection._get_config_item("VECTICE_API_ENDPOINT", config)
        except ValueError:
            _logger.debug(f"No VECTICE_API_ENDPOINT provided. Using default endpoint {DEFAULT_API_ENDPOINT}")
            return DEFAULT_API_ENDPOINT

    @staticmethod
    def _get_api_token(host: str | None, config: str | None) -> str:
        try:
            return Connection._get_config_item("VECTICE_API_TOKEN", config)
        except ValueError as error:
            raise ValueError(
                f"You must provide the api_token. You can generate them by going to the page {host}/account/api-keys"
            ) from error

    @staticmethod
    def _get_workspace(config) -> str | None:
        try:
            return Connection._get_config_item("WORKSPACE", config)
        except ValueError:
            return None

    @staticmethod
    def _get_project(config) -> str | None:
        try:
            return str(Connection._get_config_item("PROJECT", config))
        except ValueError:
            return None

    @staticmethod
    def _get_config_item(item_name: str, config_path: str | None) -> str:
        # search in provided config file
        with suppress(KeyError, SyntaxError, TypeError):
            config = Configuration(config_path)  # type: ignore[arg-type]
            if config[item_name]:
                _logger.debug(f"Found {item_name} in {config_path}")
                return config[item_name]
        # search in environment variables
        item = os.environ.get(item_name)
        if item:
            _logger.debug(f"Found {item_name} in environment variables.")
            return item
        # search in user configuration files
        for path in Connection.USER_FILES_PATH:
            with hide_logs("dotenv"):
                item = dotenv.get_key(path, item_name)
            if item:
                _logger.debug(f"Found {item_name} in {path}")
                return item
        raise ValueError(f"Could not find {item_name} in user configuration")

    def get_workspace(self, workspace: str, user_name: str, host: str) -> Workspace:
        workspace_output: Workspace = self.workspace(workspace)
        _logger.info(
            CONNECTION_WORKSPACE_LOGGING.format(
                user=user_name, workspace_name=workspace_output.name, url=host, workspace_id=workspace_output.id
            )
        )
        return workspace_output

    def get_project(self, workspace: str, project: str, user_name: str, host: str) -> Project:
        workspace_output = self.workspace(workspace)
        project_output: Project = workspace_output.project(project)
        _logger.info(
            CONNECTION_PROJECT_LOGGING.format(
                user=user_name,
                project_name=project_output.name,
                url=host,
                workspace_id=workspace_output.id,
                project_id=project_output.id,
            )
        )
        return project_output
