from io import IOBase

from PIL.Image import Image

from vectice.utils.common_utils import _check_image_path


def is_image(value):
    return is_pil_image(value) or is_binary(value) or is_existing_image_path(value)


def is_pil_image(value):
    return value if isinstance(value, Image) else None


def is_binary(value):
    return value if isinstance(value, IOBase) else None


def is_existing_image_path(value):
    return value if isinstance(value, str) and _check_image_path(value) else None
