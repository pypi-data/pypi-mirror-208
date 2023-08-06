from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, NoReturn

from vectice.utils.vectice_ids_regex import ITERATION_VID_REG, PHASE_VID_REG, PROJECT_VID_REG, WORKSPACE_VID_REG

if TYPE_CHECKING:
    from gql.transport.exceptions import TransportQueryError

    from vectice.api.http_error import HttpError

BAD_OR_MISSING_CREDENTIALS_ERROR_MESSAGE = "Bad or missing credentials"


class InvalidIdError(ValueError):
    """When an incorrect value type is passed at the client level."""

    def __init__(self, reference_type: str, value: Any) -> None:
        valid_id = "a valid id"
        wsp = "WSP-[int]"
        prj = "PRJ-[int]"
        pha = "PHA-[int]"
        itr = "ITR-[int]"
        dts = "DTS-[int]"
        dsv = "DTV-[int]"
        mod = "MDL-[int]"
        mdv = "MDV-[int]"
        if reference_type == "workspace":
            valid_id = wsp
        elif reference_type == "project":
            valid_id = prj
        elif reference_type == "phase":
            valid_id = pha
        elif reference_type == "iteration":
            valid_id = itr
        elif reference_type == "dataset":
            valid_id = dts
        elif reference_type == "dataset_version":
            valid_id = dsv
        elif reference_type == "model":
            valid_id = mod
        elif reference_type == "model_version":
            valid_id = mdv
        elif reference_type == "asset":
            refs = {", ".join([wsp, prj, pha, itr, dts, dsv, mod, mdv])}
            valid_id = f"one of ({refs})"

        super().__init__(
            f"The {reference_type} reference is invalid. Please check the provided value. "
            + f"It should be {valid_id} "
            + f"Provided value is {value}"
        )


class InvalidReferenceError(ValueError):
    """When an incorrect value type is passed at the client level."""

    def __init__(self, reference_type: str, value: Any) -> None:
        super().__init__(
            f"The {reference_type} reference is invalid."
            + "Please check the provided value as it should be a string or a number."
            + f"Provided value is {value} ({type(value)})"
        )


class MissingReferenceError(ValueError):
    """When a value is missing at the client level."""

    def __init__(self, reference_type: str, parent_reference_type: str | None = None) -> None:
        if parent_reference_type is not None:
            super().__init__(f"The {parent_reference_type} reference is required if the {reference_type} name is given")
        else:
            super().__init__(f"The {reference_type} reference is required")


class ClientErrorHandler:
    def _graphql_error_formatter(self, error: TransportQueryError) -> Exception:
        exception = error.errors[0]["extensions"]["exception"]  # type: ignore
        if "stacktrace" in exception:
            # try to format the message
            message = exception["stacktrace"]
            message = message[0].split(":")
            error_code = message[0]
            error_message = message[1]
            raise VecticeException(f"{error_code}: {error_message}")
        # just dump the stringified error
        raise VecticeException(repr(exception))

    def handle_code(self, e: HttpError, reference_type: str, reference: str | int) -> NoReturn:
        if e.code == 404:
            raise BadReferenceFactory.get_reference(reference_type, reference)
        elif e.code == 401:
            raise ConnectionRefusedError(BAD_OR_MISSING_CREDENTIALS_ERROR_MESSAGE)
        elif e.code == 403:
            raise PermissionError(f"Missing permissions to access this {reference_type}")
        raise RuntimeError(f"Can not access {reference_type}: {e.reason}")

    def handle_get_http_error(self, e: HttpError, reference_type: str, reference: str | int) -> NoReturn:
        self.handle_code(e, reference_type, reference)

    def handle_put_http_error(self, e: HttpError, reference_type: str, reference: str | int) -> NoReturn:
        self.handle_code(e, reference_type, reference)

    def handle_delete_http_error(self, e: HttpError, reference_type: str, reference: str | int) -> NoReturn:
        self.handle_code(e, reference_type, reference)

    def handle_post_http_error(self, e: HttpError, reference_type: str, action: str = "create") -> NoReturn:
        if e.code == 401:
            raise ConnectionRefusedError(BAD_OR_MISSING_CREDENTIALS_ERROR_MESSAGE)
        elif e.code == 403:
            raise PermissionError(f"Missing permissions to access this {reference_type}")
        elif e.code == 400:
            raise RuntimeError(f"Can not {action} {reference_type}: {e.reason}")
        raise RuntimeError(f"Unexpected error: {e.reason}")

    def handle_post_gql_error(self, error: TransportQueryError, reference_type: str, reference: str | int) -> NoReturn:
        try:
            status_code = error.errors[0]["extensions"]["exception"]["status"]  # type: ignore[index]
        except KeyError:
            status_code = -1
        if status_code == 404:
            raise BadReferenceFactory.get_reference(reference_type, reference)
        elif status_code == 401:
            raise ConnectionRefusedError(BAD_OR_MISSING_CREDENTIALS_ERROR_MESSAGE)
        elif status_code == 403:
            raise PermissionError(f"Missing permissions to access this {reference_type}")
        elif status_code == 400 or status_code == 412:
            # backend always adds a "message" to the response
            message = error.errors[0]["message"]  # type: ignore
            raise VecticeException(f"{reference_type}: {message}")
        raise self._graphql_error_formatter(error) from error


class BadReferenceFactory:
    """Appropriate exceptions for HTTP/GQL errors."""

    @classmethod
    def get_reference(cls, reference_type: str, value: str | int) -> Exception:
        """Get an appropriate error given a reference type.

        Parameters:
            reference_type: The reference type.
            value: A value.

        Returns:
            An exception instance.
        """
        if isinstance(value, str) and reference_type == "workspace":
            if not re.search(WORKSPACE_VID_REG, value):
                return WorkspaceNameError(value)
            return WorkspaceIdError(value)
        elif isinstance(value, str) and reference_type == "project":
            if not re.search(PROJECT_VID_REG, value):
                return ProjectNameError(value)
            return ProjectIdError(value)
        elif isinstance(value, str) and reference_type == "phase":
            if not re.search(PHASE_VID_REG, value):
                return PhaseNameError(value)
            return PhaseIdError(value)
        elif reference_type == "step":
            if isinstance(value, str):
                return StepNameError(value)
            elif isinstance(value, int):
                return StepIdError(value)
        elif isinstance(value, str) and reference_type == "iteration":
            if re.search(ITERATION_VID_REG, value):
                return IterationIdError(value)
            return IterationNameError(value)
        elif reference_type == "iteration_index":
            if isinstance(value, int):
                return IterationIndexError(value)
        elif isinstance(value, str) and reference_type == "steps":
            return NoStepsInPhaseError(value)
        elif isinstance(value, str) and reference_type == "dataset":
            return DatasetIdError(value)
        elif isinstance(value, str) and reference_type == "dataset_version":
            return DatasetVersionIdError(value)
        elif isinstance(value, str) and reference_type == "model":
            return ModelIdError(value)
        elif isinstance(value, str) and reference_type == "model_version":
            return ModelVersionIdError(value)
        return RuntimeError(f"The value {value} of type {reference_type} is not valid!")


class VecticeException(Exception):  # noqa: N818
    def __init__(self, value):
        super().__init__(value)
        self.__suppress_context__ = True
        self.value = value


class VecticeBaseNameError(NameError):
    def __init__(self, value):
        super().__init__(value)
        self.__suppress_context__ = True
        self.value = value

    def __str__(self):
        divider = "=" * len(f"{self.__class__.__name__}: {self.value}")
        return f"\n{divider}\n{self.__class__.__name__}: {self.value}"


class WorkspaceNameError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The workspace with name '{value}' is unknown.")


class WorkspaceIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The workspace with id '{value}' is unknown.")


class ProjectNameError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The project with name '{value}' is unknown.")


class ProjectIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The project with id '{value}' is unknown.")


class PhaseNameError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The phase with name '{value}' is unknown.")


class PhaseIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The phase with id '{value}' is unknown.")


class StepNameError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(
            f"The step with name '{value}' is unknown. Use <your iteration>.list_steps() method to find step names."
        )


class StepIdError(VecticeBaseNameError):
    def __init__(self, value: int):
        super().__init__(
            f"The step with id '{value}' is unknown. Use <your iteration>.list_steps() method to find step ids."
        )


class IterationIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The iteration with id '{value}' is unknown.")


class IterationIndexError(VecticeBaseNameError):
    def __init__(self, value: int):
        super().__init__(f"The iteration with index '{value}' is unknown.")


class IterationNameError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The iteration with name '{value}' is unknown.")


class NoStepsInPhaseError(VecticeBaseNameError):
    def __init__(self, value: str):
        ref = f"with id '{value}'" if re.search(PHASE_VID_REG, value) else f"'{value}'"
        super().__init__(f"There are no steps in the phase {ref}. Must create steps for this phase in the UI.")


class DatasetIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The dataset with id '{value}' is unknown.")


class DatasetVersionIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The dataset version with id '{value}' is unknown.")


class ModelIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The model with id '{value}' is unknown.")


class ModelVersionIdError(VecticeBaseNameError):
    def __init__(self, value: str):
        super().__init__(f"The model version with id '{value}' is unknown.")
