from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

from git import GitError
from git.repo import Repo

import vectice
from vectice.api.json.code import CodeInput
from vectice.api.json.code_version import CodeVersionCreateBody, GitVersion
from vectice.utils.common_utils import hide_logs

if TYPE_CHECKING:
    from logging import Logger

    from git.diff import Diff

    from vectice.api.client import Client
    from vectice.api.json.user_declared_version import UserDeclaredVersion


_logger = logging.getLogger(__name__)


class CodeSource:
    """Capture the current git commit."""

    def __init__(self, repository: Repo, user_declared_version: UserDeclaredVersion | None = None):
        self._repository: Repo = repository
        self._git_version: GitVersion | None = _extract_git_version(repository)
        self._user_declared_version: UserDeclaredVersion | None = user_declared_version

    @property
    def repository(self) -> Any:
        return self._repository

    @property
    def user_declared_version(self) -> UserDeclaredVersion | None:
        return self._user_declared_version

    @property
    def git_version(self) -> GitVersion | None:
        return self._git_version


def _check_code_source(client: Client, project_id: str, _logger: Logger) -> int | None:
    """Capture source code.

    Naive implementation that uses the commit hash to name the code.

    Only one version of the code is stored in backend.
    This allows to easily reuse versions based on their commits hash.

    Parameters:
        client: The Vectice client, used to communicate with the backend.
        project_id: The id of the current project.

    Returns:
        Either the id of the created/fetched code version, or none if the code could not be captured.
    """
    repository = _look_for_git_repository()
    if not repository:
        return None
    code = CodeSource(repository)
    if not code.git_version:
        return None
    code_input = CodeInput(name=code.git_version.commitHash)
    try:
        code_output = client.create_code_gql(project_id, code_input)
    except Exception:
        code_output = client.get_code(code.git_version.commitHash, project_id)
        code_version_output = client.get_code_version("Version 1", code_output.id)
        _logger.debug("The code commit exists already.")
        return int(code_version_output.id)
    if code.user_declared_version:
        user_declared_version = code.user_declared_version.__dict__
    else:
        user_declared_version = {}
    code_version_body = CodeVersionCreateBody(
        action="CREATE_GIT_VERSION", gitVersion=code.git_version.__dict__, userDeclaredVersion=user_declared_version
    )
    code_version_output = client.create_code_version_gql(code_output.id, code_version_body)
    _logger.debug("Code captured and will be linked to asset.")
    code_version_id = int(code_version_output.id)
    _capture_local_changed_files(repository, client, project_id, code_version_id)
    return code_version_id


def _capture_local_changed_files(repository: Repo, client: Client, project_id: str, code_version_id: int) -> None:
    diff_outputs = []
    file_names = []
    try:
        changed_files: list[Diff] = repository.index.diff(None)
    except Exception as error:
        changed_files = []
        _logger.warning(
            "Capturing local changed files failed: "
            f"we couldn't get the diff from last commit (detached mode? no commits?): {error!r}"
        )
    for file in changed_files:
        try:
            diff = repository.git.diff(file.a_path)
        except Exception:
            _logger.warning(f"Capturing diff failed for file: {file.a_path}")
            continue
        diff_outputs.append(("file", (f"{file.a_path}.diff", (diff))))
        if file.a_path is not None:
            file_names.append(file.a_path)
    if diff_outputs:
        client.create_code_attachments(diff_outputs, code_version_id, project_id)
    if file_names:
        _logger.info(f"Code captured the following changed files; {', '.join(file_names)}")


def _look_for_git_repository(repo_path=".") -> Any | None:
    try:
        repo_path = os.path.abspath(repo_path)
    except OSError:
        _logger.debug(f"Code capture failed: the directory '{repo_path}' cannot be accessed by the system")
        return None
    try:
        return Repo(repo_path, search_parent_directories=True)
    except GitError as error:
        error_message = str(error) or repo_path
        _logger.debug(
            f"Code capture failed: {error.__class__.__name__}: {error_message}. "
            "Make sure the current directory is a valid Git repository (non-bare, non worktree) "
            "and its permissions allow the current user to access it."
        )
        return None


def _check_for_code(client: Client, project_id: str, _logger: Logger) -> int | None:
    code_version_id = None

    if vectice.code_capture:
        code_version_id = _check_code_source(client, project_id, _logger)
    return code_version_id


def _inform_if_git_repo():
    with hide_logs("vectice"):
        repo = _look_for_git_repository()
    if repo:
        _logger.debug("A git repository was found but code capture is disabled.")


def _extract_git_version(repository: Repo) -> GitVersion | None:
    prefix = "Extracting the Git version failed"
    try:
        url = repository.remotes.origin.url
    except Exception as error:
        _logger.warning(f"{prefix}: we couldn't get the remote URL (no origin?): {error!r}")
        return None
    url = url.rsplit(".git", 1)[0]
    repository_name = url.split("/")[-1]
    try:
        branch_name = repository.active_branch.name
    except Exception as error:
        _logger.warning(f"{prefix}: we couldn't get the branch name (detached mode?): {error!r}")
        return None
    try:
        commit_hash = repository.head.object.hexsha
    except Exception as error:
        _logger.warning(f"{prefix}: we couldn't get the commit hash (no commits?): {error!r})")
        return None
    is_dirty = repository.is_dirty()
    return GitVersion(repository_name, branch_name, commit_hash, is_dirty, url)
