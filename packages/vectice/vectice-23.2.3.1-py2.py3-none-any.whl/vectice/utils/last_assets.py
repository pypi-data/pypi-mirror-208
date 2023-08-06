from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING, Any

from vectice.utils.automatic_link_utils import existing_dataset_logger, existing_model_logger

if TYPE_CHECKING:
    from logging import Logger

    from vectice.api import Client
    from vectice.api.json.last_assets import ActivityTargetType
    from vectice.models.step import Step


def _get_last_assets(target_types: list[ActivityTargetType], client: Client, _logger: Logger):
    target_types_array = [target.value for target in target_types]
    try:
        last_asset = client.get_last_assets(target_types_array, {"index": 1, "size": 1}).list[0]
        return last_asset
    except IndexError as e:
        _logger.debug(f"There were no assets with activity found. Sanity check {e}")
        return


def _get_last_user_and_default_workspace(client: Client) -> tuple[str, str | None]:
    asset = client.get_user_and_default_workspace()
    workspace_id = str(asset["defaultWorkspace"]["vecticeId"]) if asset["defaultWorkspace"] else None
    return asset["user"]["name"], workspace_id


def _connection_logging(_logger: Logger, user_name: str, host: str, workspace_id: str | None):
    from vectice.utils.logging_utils import CONNECTION_LOGGING

    if workspace_id:
        logging_output = f"For quick access to your default workspace in the Vectice web app, visit:\n{host}/browse/workspace/{workspace_id}"
        _logger.info(CONNECTION_LOGGING.format(user=user_name, logging_output=logging_output))
        return
    logging_output = f"For quick access to the list of workspaces in the Vectice web app, visit:\n{host}/workspaces"
    _logger.info(CONNECTION_LOGGING.format(user=user_name, logging_output=logging_output))


def _register_dataset_logging(
    step: Step, data: dict, value: Any, attachments, _logger: Logger, step_artifacts: Any | None = None
):
    iteration_id = step._iteration.id
    url = step._client.auth.api_base_url
    hyper_link = f"{url}/browse/iteration/{iteration_id}"

    # check if exists
    existing_logging = existing_dataset_logger(data, value.name, _logger)
    # check if attached to step
    check_artifacts = step_artifacts if step_artifacts else step.artifacts
    match = next(filter(lambda x: x.dataset_version_id == data["datasetVersion"]["vecticeId"], check_artifacts), None)
    attachments_output = None
    if attachments:
        attachments_output = ", ".join([attach["fileName"] for attach in attachments])
    logging_output = None
    if existing_logging and match:
        logging_output = dedent(
            f"""
                                Existing Dataset: {value.name!r} and Version: {data['datasetVersion']['name']!r} already linked to Step: {step.name}
                                Attachments: {attachments_output}
                                Link to Step: {hyper_link}
                                """
        ).lstrip()
    if existing_logging and not match:
        logging_output = dedent(
            f"""
                    New Version: {data['datasetVersion']['name']!r} of Dataset: {value.name!r} added to Step: {step.name}
                    Attachments: {attachments_output}
                    Link to Step: {hyper_link}
                    """
        ).lstrip()
    if not existing_logging and not match:
        logging_output = dedent(
            f"""
                                    New Dataset: {value.name!r} Version: {data['datasetVersion']['name']!r} added to Step: {step.name}
                                    Attachments: {attachments_output}
                                    Link to Step: {hyper_link}
                                    """
        ).lstrip()
    if logging_output:
        _logger.info(logging_output)
    else:
        _logger.debug("Logging failed for register dataset at step, check _register_dataset_logging.")


def _comment_or_image_logging(step: Step, _logger: Logger, filename: str | None = None):
    iteration_id = step._iteration.id
    url = step._client.auth.api_base_url
    hyper_link = f"{url}/browse/iteration/{iteration_id}"
    if filename:
        artifact_reference = f"Image: {filename!r}"
    else:
        artifact_reference = "Comment"
    logging_output = dedent(
        f"""
        Added {artifact_reference} to Step: {step.name}

        Link to Step: {hyper_link}
        """
    ).lstrip()

    _logger.info(logging_output)


def _register_model_logging(
    step: Step, data: dict, value: Any, step_name: str, attachments, _logger: Logger, step_artifacts: Any | None = None
):
    iteration_id = step._iteration.id
    url = step._client.auth.api_base_url
    hyper_link = f"{url}/browse/iteration/{iteration_id}"

    # check if exists
    existing_logging = existing_model_logger(data, value.name, _logger)
    # check if attached to step already
    check_artifacts = step_artifacts if step_artifacts else step.artifacts
    match = next(filter(lambda x: x.model_version_id == data["modelVersion"]["vecticeId"], check_artifacts), None)
    attachments_output = None
    if attachments:
        attachments_output = ", ".join([attach["fileName"] for attach in attachments])
    logging_output = None
    if existing_logging and match:
        logging_output = dedent(
            f"""
                                Existing Model: {value.name!r} and Version: {data['modelVersion']['name']!r} already linked to Step: {step_name}
                                Attachments: {attachments_output}
                                Link to Step: {hyper_link}
                                """
        ).lstrip()
    if existing_logging and not match:
        logging_output = dedent(
            f"""
                    New Version: {data['modelVersion']['name']!r} of Model: {value.name!r} added to Step: {step_name}
                    Attachments: {attachments_output}
                    Link to Step: {hyper_link}
                    """
        ).lstrip()
    if not existing_logging and not match:
        logging_output = dedent(
            f"""
                                    New Model: {value.name!r} Version: {data['modelVersion']['name']!r} added to Step: {step_name}
                                    Attachments: {attachments_output}
                                    Link to Step: {hyper_link}
                                    """
        ).lstrip()

    if logging_output:
        _logger.info(logging_output)
    else:
        _logger.debug("Logging failed for register model at step, check _register_model_logging.")
