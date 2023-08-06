from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import TYPE_CHECKING, BinaryIO

from gql import Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport

from vectice.__version__ import __version__
from vectice.api._auth import Auth
from vectice.api.attachment import AttachmentApi
from vectice.api.compatibility import CompatibilityApi
from vectice.api.gql_code import GqlCodeApi
from vectice.api.gql_code_version import GqlCodeVersionApi
from vectice.api.gql_dataset import GqlDatasetApi
from vectice.api.gql_feature_flag import GqlFeatureFlagApi
from vectice.api.gql_model import GqlModelApi
from vectice.api.gql_user_workspace_api import UserAndDefaultWorkspaceApi
from vectice.api.http_error_handlers import MissingReferenceError, VecticeException
from vectice.api.iteration import IterationApi
from vectice.api.json import (
    ArtifactName,
    CodeInput,
    CodeVersionCreateBody,
    ModelRegisterInput,
    ModelRegisterOutput,
    ModelType,
    ModelVersionOutput,
    ModelVersionStatus,
    Page,
    PagedResponse,
    PropertyInput,
    StepOutput,
)
from vectice.api.json.dataset_register import DatasetRegisterInput, DatasetRegisterOutput
from vectice.api.json.dataset_representation import DatasetRepresentationOutput
from vectice.api.json.dataset_version import DatasetVersionOutput
from vectice.api.json.dataset_version_representation import DatasetVersionRepresentationOutput
from vectice.api.json.metric import MetricInput
from vectice.api.json.model_representation import ModelRepresentationOutput
from vectice.api.json.model_version_representation import ModelVersionRepresentationOutput
from vectice.api.last_assets import LastAssetApi
from vectice.api.phase import PhaseApi
from vectice.api.project import ProjectApi
from vectice.api.step import StepApi
from vectice.api.version import VersionApi
from vectice.api.workspace import WorkspaceApi
from vectice.models.dataset import Dataset
from vectice.models.representation.dataset_version_representation import DatasetVersionRepresentation
from vectice.models.representation.model_version_representation import ModelVersionRepresentation
from vectice.utils.vectice_ids_regex import WORKSPACE_VID_REG

if TYPE_CHECKING:
    from io import BytesIO, IOBase

    from requests import Response

    from vectice.api.json import AttachmentOutput, ProjectOutput, WorkspaceOutput
    from vectice.api.json.compatibility import CompatibilityOutput
    from vectice.api.json.iteration import IterationInput, IterationOutput, IterationStepArtifactInput
    from vectice.api.json.phase import PhaseOutput
    from vectice.api.json.step import StepType
    from vectice.models.model import Model

_logger = logging.getLogger(__name__)


DISABLED_FEATURE_FLAG_MESSAGE = (
    "This '{}' feature is not enabled. Please contact your Account Manager for Beta program access."
)


def _auth_success_message(workspace: WorkspaceOutput, project: ProjectOutput | None) -> str:
    if workspace and project:
        return f"Successfully authenticated. You'll be working on Project: '{project.name}', part of Workspace: '{workspace.name}'"
    return f"Successfully authenticated. Your current Workspace: '{workspace.name}'"


class Client:
    """Low level Vectice API client."""

    def __init__(
        self,
        workspace: str | None = None,
        project: str | None = None,
        token: str | None = None,
        api_endpoint: str | None = None,
        auto_connect=True,
        allow_self_certificate=True,
    ):
        self.auth = Auth(
            api_endpoint=api_endpoint,
            api_token=token,
            auto_connect=auto_connect,
            allow_self_certificate=allow_self_certificate,
        )
        transport = RequestsHTTPTransport(url=self.auth.api_base_url + "/graphql", verify=self.auth.verify_certificate)
        logging.getLogger("gql.transport.requests").setLevel("WARNING")
        self._gql_client = GQLClient(transport=transport)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._workspace: WorkspaceOutput | None = None
        self._project: ProjectOutput | None = None

        if auto_connect:
            if workspace and project:
                self._project = self.get_project(project, workspace)
                self._workspace = self._project.workspace
                is_vectice_id = re.search(WORKSPACE_VID_REG, workspace)
                if (not is_vectice_id and workspace != self._workspace.name) or (
                    is_vectice_id and workspace != self._workspace.id
                ):
                    raise ValueError(
                        f"Inconsistency in configuration: Project {project} does not belong to Workspace {workspace}"
                    )
            elif workspace:
                self._workspace = self.get_workspace(workspace)
            elif project:
                self._project = self.get_project(project)
                self._workspace = self._project.workspace

            if self._workspace:
                _logger.debug(_auth_success_message(workspace=self._workspace, project=self._project))

    @property
    def workspace(self) -> WorkspaceOutput | None:
        """The workspace object.

        Returns:
            The workspace object.
        """
        return self._workspace

    @property
    def project(self) -> ProjectOutput | None:
        """The project object.

        Returns:
            The project object.
        """
        return self._project

    @property
    def version_api(self) -> str:
        return __version__

    @property
    def version_backend(self) -> str:
        versions = VersionApi(self._gql_client, self.auth).get_public_config().versions
        for version in versions:
            if version.artifact_name == ArtifactName.BACKEND:
                return version.version
        raise ValueError("No version found for backend.")

    def check_compatibility(self) -> CompatibilityOutput:
        return CompatibilityApi(self.auth).check_version()

    def list_projects(
        self,
        workspace: str,
        search: str | None = None,
        page_index: int | None = Page.index,
        page_size: int | None = Page.size,
    ) -> list[ProjectOutput]:
        """List the projects in a workspace.

        Parameters:
            workspace: The workspace name or id.
            search: A text to search for.
            page_index: The index of the page.
            page_size: The size of the page.

        Returns:
            The workspace's projects.
        """
        if not re.search(WORKSPACE_VID_REG, workspace):
            workspace = WorkspaceApi(self._gql_client, self.auth).get_workspace(workspace).id
        return ProjectApi(self._gql_client, self.auth).list_projects(workspace, search, page_index, page_size)

    def get_project(self, project: str, workspace: str | None = None) -> ProjectOutput:
        """Get a project.

        Parameters:
            project: The project name or vectice id.
            workspace: The workspace name or id.

        Returns:
            The project JSON structure.
        """
        if workspace is not None and not re.search(WORKSPACE_VID_REG, workspace):
            workspace = WorkspaceApi(self._gql_client, self.auth).get_workspace(workspace).id
        return ProjectApi(self._gql_client, self.auth).get_project(project, workspace)

    def get_workspace(self, workspace: str) -> WorkspaceOutput:
        """Get a workspace.

        Parameters:
            workspace: The workspace name or id.

        Returns:
            The workspace JSON structure.
        """
        return WorkspaceApi(self._gql_client, self.auth).get_workspace(workspace)

    def list_workspaces(
        self, search: str | None = None, page_index: int = 1, page_size: int = 100
    ) -> list[WorkspaceOutput]:
        """List the workspaces.

        Parameters:
            search: A text to search for.
            page_index: The index of the page.
            page_size: The size of the page.

        Returns:
            The workspaces.
        """
        return WorkspaceApi(self._gql_client, self.auth).list_workspaces(search, page_index, page_size)

    def create_code_attachments(self, files: list[tuple[str, tuple[str, str]]], code_version_id: int, project_id: str):
        """Create an attachment.

        Parameters:
            files: The paths to the files to attach.
            code_version_id: The code version id to attach files to.
            project_id: The project id associated to the code version id.

        Returns:
            The JSON structure.
        """
        return AttachmentApi(self.auth).create_attachments(files, project_id, code_version_id=code_version_id)

    def create_version_attachments(
        self, files: list[tuple[str, tuple[str, BinaryIO]]], version: ModelVersionOutput | DatasetVersionOutput
    ):
        """Create an attachment.

        Parameters:
            files: The paths to the files to attach.
            version: The version to attach files to.

        Returns:
            The JSON structure.
        """
        return AttachmentApi(self.auth).post_attachment(files, version)

    def create_phase_attachments(
        self, files: list[tuple[str, tuple[str, BytesIO | IOBase]]], phase_id: str, project_id: str
    ) -> list[dict]:
        """Create an attachment.

        Parameters:
            files: The paths to the files to attach.
            phase_id: The phase id to attach files to.
            project_id: The project id to attach files to.

        Returns:
            The JSON structure.
        """
        return AttachmentApi(self.auth).create_attachments(files, project_id, phase_id=phase_id)

    def create_model_predictor(self, model_type: str, model_content: BytesIO, model_version: ModelVersionOutput):
        """Create a predictor.

        Parameters:
            model_type: The type of model to attach.
            model_content: The binary content of the model.
            model_version: The model version to attach files to.

        Returns:
            The JSON structure.
        """
        return AttachmentApi(self.auth).post_model_predictor(model_type, model_content, model_version)

    def list_version_representation_attachments(
        self, project_id: str, version: ModelVersionRepresentation | DatasetVersionRepresentation
    ) -> PagedResponse[AttachmentOutput]:
        """List the attachments of an artifact.

        Parameters:
            version: The version to list attachments from.

        Returns:
            The attachments of an artifact.
        """
        return AttachmentApi(self.auth).list_version_representation_attachments(project_id, version)

    def list_attachments(self, version: ModelVersionOutput | DatasetVersionOutput) -> PagedResponse[AttachmentOutput]:
        """List the attachments of an artifact.

        Parameters:
            version: The version to list attachments from.

        Returns:
            The attachments of an artifact.
        """
        return AttachmentApi(self.auth).list_attachments(version)

    def list_code_attachments(self, code_version_id: int, project_id: str) -> PagedResponse[AttachmentOutput]:
        """List the attachments of a code version.

        Parameters:
            code_version_id: The id of the code version to list attachments from.
            project_id: The id of the project the code version belongs to.

        Returns:
            A list of attachments that belong to the code version.
        """
        return AttachmentApi(self.auth).list_object_attachments(project_id, code_version_id=code_version_id)

    def list_phase_attachments(self, phase_id: str, project_id: str) -> PagedResponse[AttachmentOutput]:
        """List the attachments of a phase.

        Parameters:
            phase_id: The id of the phase the attachments belongs to.
            project_id: The id of the project the attachments belongs to.

        Returns:
            An attachment.
        """
        return AttachmentApi(self.auth).list_object_attachments(project_id, phase_id=phase_id)

    def get_code_version_attachment(self, code_version_id: int, project_id: str, file_id: int) -> Response:
        """Get the attachment of a code version.

        Parameters:
            code_version_id: The code version id to list attachments from.
            project_id: The project id the code version belongs to.
            file_id: The file id attached to the code version.

        Returns:
            The file attached to the code version.
        """
        return AttachmentApi(self.auth).get_code_version_attachment(code_version_id, project_id, file_id)

    def list_phases(
        self,
        project: str,
    ) -> PagedResponse[PhaseOutput]:
        return PhaseApi(self._gql_client, self.auth).list_phases(project)

    def get_phase(self, phase: str, project_id: str | None = None) -> PhaseOutput:
        if project_id is None:
            raise MissingReferenceError("project")
        return PhaseApi(self._gql_client, self.auth).get_phase(phase, project_id)

    def get_full_phase(self, phase: str) -> PhaseOutput:
        return PhaseApi(self._gql_client, self.auth).get_phase(phase=phase, full=True)

    def get_step_by_name(self, step_reference: str, iteration_id: str) -> StepOutput:
        return StepApi(self._gql_client, self.auth).get_step(step_reference, iteration_id)

    def list_steps(
        self,
        iteration_id: str,
    ) -> list[StepOutput]:
        return StepApi(self._gql_client, self.auth).list_steps(iteration_id)

    def add_iteration_step_artifact(self, step_id: int, step_artifacts: IterationStepArtifactInput) -> StepOutput:
        return StepApi(self._gql_client, self.auth).add_iteration_step_artifact(step_artifacts, step_id)

    def update_iteration_step_artifact(
        self,
        step_id: int,
        step_type: StepType,
        artifacts: list[IterationStepArtifactInput] | None = None,
    ) -> StepOutput:
        return StepApi(self._gql_client, self.auth).update_iteration_step_artifact(step_id, step_type, artifacts)

    def list_iterations(self, phase: str, only_mine: bool = False) -> PagedResponse[IterationOutput]:
        return IterationApi(self._gql_client, self.auth).list_iterations(phase, only_mine)

    def list_step_definitions(self, phase: str) -> list[StepOutput]:
        return PhaseApi(self._gql_client, self.auth).list_step_definitions(phase)

    def get_full_iteration(self, iteration_id: str) -> IterationOutput:
        return IterationApi(self._gql_client, self.auth).get_iteration(iteration_id, full=True)

    def get_iteration(self, iteration_id: str) -> IterationOutput:
        return IterationApi(self._gql_client, self.auth).get_iteration(iteration_id)

    def get_iteration_by_index(self, phase_id: str, index: int) -> IterationOutput:
        return IterationApi(self._gql_client, self.auth).get_iteration_by_index(phase_id, index)

    def get_iteration_last_assets(self, iteration_id: int) -> IterationOutput:
        return IterationApi(self._gql_client, self.auth).get_iteration_last_assets(iteration_id)

    def create_iteration(self, phase_id: str) -> IterationOutput:
        return IterationApi(self._gql_client, self.auth).create_iteration(phase_id)

    def update_iteration(self, iteration_id: str, iteration: IterationInput) -> IterationOutput:
        return IterationApi(self._gql_client, self.auth).update_iteration(iteration, iteration_id)

    def delete_iteration(self, iteration_id: str) -> None:
        IterationApi(self._gql_client, self.auth).delete_iteration(iteration_id)

    def register_dataset_from_source(
        self,
        dataset: Dataset,
        project_id: str | None = None,
        phase_id: str | None = None,
        iteration_id: str | None = None,
        code_version_id: int | None = None,
    ) -> DatasetRegisterOutput:
        if dataset._has_bigquery_resource and self.is_feature_flag_enabled("bigquery-dataset-source") is False:
            raise VecticeException(DISABLED_FEATURE_FLAG_MESSAGE.format("bigquery-dataset-source"))

        if dataset._has_dataframe is True and self.is_feature_flag_enabled("dataset-dataframe") is False:
            raise VecticeException(DISABLED_FEATURE_FLAG_MESSAGE.format("dataset-dataframe"))

        name = self.get_dataset_name(dataset)
        derived_from = self.get_derived_from(dataset)
        if isinstance(dataset.resource, tuple):
            # modeling dataset
            metadata_asdict = [data_source.metadata.asdict() for data_source in dataset.resource if data_source]
        else:
            metadata_asdict = [dataset.resource.metadata.asdict()]

        properties = (
            [vars(PropertyInput(prop.key, prop.value)) for prop in dataset.properties] if dataset.properties else None
        )

        dataset_register_input = DatasetRegisterInput(
            name=name,
            type=dataset.type.value,
            datasetSources=metadata_asdict,
            inputs=derived_from,
            codeVersionId=code_version_id,
            properties=properties,
        )
        dataset_register_output = self.register_dataset(dataset_register_input, project_id, phase_id, iteration_id)
        dataset.latest_version_id = dataset_register_output["datasetVersion"]["vecticeId"]
        return dataset_register_output

    def get_dataset(self, id: str) -> DatasetRepresentationOutput:
        return GqlDatasetApi(self._gql_client, self.auth).get_dataset(id)

    def get_dataset_version(self, id: str) -> DatasetVersionRepresentationOutput:
        return GqlDatasetApi(self._gql_client, self.auth).get_dataset_version(id)

    def get_model(self, id: str) -> ModelRepresentationOutput:
        return GqlModelApi(self._gql_client, self.auth).get_model(id)

    def get_model_version(self, id: str) -> ModelVersionRepresentationOutput:
        return GqlModelApi(self._gql_client, self.auth).get_model_version(id)

    @staticmethod
    def get_dataset_name(dataset: Dataset) -> str:
        return f"dataset {datetime.time}" if dataset.name is None else dataset.name

    @staticmethod
    def get_derived_from(obj: Dataset | Model) -> list[str]:
        return [] if obj.derived_from is None else obj.derived_from

    def register_dataset(
        self,
        dataset_register_input: DatasetRegisterInput,
        project_id: str | None = None,
        phase_id: str | None = None,
        iteration_id: str | None = None,
    ) -> DatasetRegisterOutput:
        data: DatasetRegisterOutput = GqlDatasetApi(self._gql_client, self.auth).register_dataset(
            dataset_register_input, project_id, phase_id, iteration_id
        )
        _logger.debug(
            f"Successfully registered Dataset("
            f"name='{dataset_register_input.name}', "
            f"id={data['datasetVersion']['vecticeId']}, "
            f"version='{data['datasetVersion']['name']}', "
            f"type={dataset_register_input.type})."
        )
        return data

    def get_project_and_workspace_references(self, project: str | None = None, workspace: str | None = None):
        if project is None and self.project is not None:
            project = self.project.id
        if workspace is None and self.workspace is not None:
            workspace = self.workspace.id
        return project, workspace

    def get_project_and_workspace_references_or_raise_error(
        self, project: str | None = None, workspace: str | None = None
    ) -> tuple[str, str | None]:
        project, workspace = self.get_project_and_workspace_references(project, workspace)
        if project is None:
            raise MissingReferenceError("project")
        return project, workspace

    @staticmethod
    def _get_model_name(library: str, technique: str, name: str | None = None) -> str:
        return name if name else f"{library} {technique} model"

    def register_model(
        self,
        model: Model,
        project_id: str,
        phase_id: str | None = None,
        iteration_id: str | None = None,
        code_version_id: int | None = None,
    ) -> ModelRegisterOutput:
        """Register a model.

        Parameters:
            model: The model to register
            project_id: The project ID
            phase_id: The phase ID
            iteration_id: The iteration ID
            code_version_id: The code version ID

        Returns:
            The registered model.
        """
        metrics = [vars(MetricInput(metric.key, metric.value)) for metric in model.metrics] if model.metrics else None
        properties = (
            [vars(PropertyInput(prop.key, prop.value)) for prop in model.properties] if model.properties else None
        )
        derived_from = self.get_derived_from(model)
        model_register_input = ModelRegisterInput(
            name=model.name,
            modelType=ModelType.OTHER.value,
            status=ModelVersionStatus.EXPERIMENTATION.value,
            inputs=derived_from,
            metrics=metrics,
            properties=properties,
            algorithmName=model.technique,
            framework=model.library,
            codeVersionId=code_version_id,
        )
        return GqlModelApi(self._gql_client, self.auth).register_model(
            model_register_input, project_id, phase_id, iteration_id
        )

    def get_last_assets(self, target_types: list[str], page):
        return LastAssetApi(self._gql_client, self.auth).get_last_assets(target_types, page)

    def get_user_and_default_workspace(self):
        return UserAndDefaultWorkspaceApi(self._gql_client, self.auth).get_user_and_default_workspace()

    def create_code_gql(self, project_id: str, code: CodeInput):
        return GqlCodeApi(self._gql_client, self.auth).create_code(project_id, code)

    def create_code_version_gql(self, code_id: int, code_version: CodeVersionCreateBody):
        return GqlCodeVersionApi(self._gql_client, self.auth).create_code_version(code_id, code_version)

    def get_code(self, code: str | int, project_id: str | None = None):
        if project_id is None:
            raise MissingReferenceError("project")
        return GqlCodeApi(self._gql_client, self.auth).get_code(code, project_id)

    def get_code_version(self, code_version: str | int, code_id: int | None = None):
        if code_id is None:
            raise MissingReferenceError("code")
        return GqlCodeVersionApi(self._gql_client, self.auth).get_code_version(code_version, code_id)

    def is_feature_flag_enabled(self, code: str) -> bool:
        enabled = GqlFeatureFlagApi(self._gql_client, self.auth).is_feature_flag_enabled(code)
        if enabled is False:
            _logger.info(DISABLED_FEATURE_FLAG_MESSAGE.format(code))
        return enabled
