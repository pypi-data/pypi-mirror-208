"""lxmlh."""
import importlib.metadata
from typing import Union

from .config import TIMESTAMP_FORMAT, TYPE_DEFAULTS, TYPE_FUNC_MAP
from .helpers import (
    create_attribute,
    create_attribute_list,
    create_element_text,
    fill_in_defaults,
    get_element,
    get_element_list,
    get_inner_text_list,
)
from .parsers import parse_directory, parse_file, save_file, validate_file

__all__ = (
    "__version__",
    "fill_in_defaults",
    "create_attribute",
    "create_element_text",
    "create_attribute_list",
    "get_element",
    "get_element_list",
    "get_inner_text_list",
    "parse_directory",
    "parse_file",
    "save_file",
    "TIMESTAMP_FORMAT",
    "TYPE_DEFAULTS",
    "TYPE_FUNC_MAP",
    "validate_file",
)


def _get_version_tuple() -> tuple:
    def as_integer(string: str) -> Union[int, str]:
        try:
            return int(string)
        except ValueError:  # pragma: no cover
            return string  # pragma: no cover

    return tuple(
        as_integer(v) for v in importlib.metadata.version("lxmlh").strip().split(".")
    )


__version__ = _get_version_tuple()
