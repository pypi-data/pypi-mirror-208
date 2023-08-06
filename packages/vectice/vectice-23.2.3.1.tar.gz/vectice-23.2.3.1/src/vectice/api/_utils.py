from __future__ import annotations

import os
from datetime import datetime

from dotenv import dotenv_values, find_dotenv


def read_nodejs_date(date_as_string: str | None) -> datetime | None:
    if date_as_string is None:
        return None
    return datetime.strptime(date_as_string, "%Y-%m-%dT%H:%M:%S.%f%z")


def calculate_duration(end_date: datetime, start_date_nodejs_format: str) -> int:
    # format sample : 2021-06-20T11:04:16.249Z
    start_date = read_nodejs_date(start_date_nodejs_format)
    if start_date is None:
        raise RuntimeError("Invalid date format for value: " + start_date_nodejs_format)
    duration = end_date - start_date
    return int(duration.total_seconds())


def read_env(*args: str) -> list[str | None]:
    """Read user configuration.

    Configuration is read from different locations, in this order:

    - `.vectice` file
    - `.env` file
    - environment variables

    As usual, system variables always take precedence over dotenv files.
    And as expected, dotenv files take precedence over dotvectice files.

    Parameters:
        *args: The keys of the configuration items to return.

    Raises:
        ValueError: When no arguments are given.

    Returns:
        A list of configuration items.
    """
    if len(args) == 0:
        raise ValueError(
            "No configuration arguments found.  At least one argument must be provided to connect to Vectice."
        )
    config: dict[str, str | None] = {
        **dotenv_values(find_dotenv(".vectice")),
        **dotenv_values(find_dotenv(".env")),
        **os.environ,
    }
    return [config.get(key) for key in args]
