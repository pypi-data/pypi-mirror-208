"""Test cases for the __parsers__ module."""
import os
import tempfile
from io import StringIO
from pathlib import Path

from lxml import etree

from lxmlh.parsers import parse_directory, save_file, validate_file

from .conftest import FILE_SAMPLE, FILE_SAMPLE_DEFAULTS, FILE_SCHEMA, Lookup


def test_parse_directory() -> None:
    """It reads all files successfully."""
    dirPath = os.path.join(Path(__file__).parent.parent.resolve(), "data")
    files = [os.path.join(dirPath, "sample.xml")]
    roots = sorted(parse_directory(dirPath, FILE_SCHEMA, Lookup()))

    assert len(roots) == 2
    assert roots[0][0] == Path(files[0])
    assert roots[0][1].shipTo.name == "Ola Nordmann"


def _compare_files(file1: str, file2: str) -> bool:
    with open(file1, encoding="utf-8") as inputFile:
        with open(file2, encoding="utf-8") as outputFile:
            mapping = {ord(c): "" for c in [" ", "\t", "\n"]}
            translatedOutput = outputFile.read().translate(mapping)
            translatedInput = inputFile.read().translate(mapping)
            return translatedOutput == translatedInput


def test_save_file(ship_order: etree.ElementTree) -> None:
    """It saves file correctly."""
    outputPath = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
    save_file(ship_order, outputPath)

    assert _compare_files(FILE_SAMPLE, outputPath)


def test_save_file_defaults(ship_order: etree.ElementTree) -> None:
    """It saves file correctly."""

    def _get_order_time(element: etree.ElementBase) -> str:
        return element.orderId

    staticDefaults = {"ShipOrder": {"orderStatus": "wip"}}
    dynamicDefaults = {"ShipOrder": {"orderTime": _get_order_time}}
    outputPath = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
    save_file(
        ship_order,
        outputPath,
        static_defaults=staticDefaults,
        dynamic_defaults=dynamicDefaults,
    )

    assert _compare_files(FILE_SAMPLE_DEFAULTS, outputPath)


def test_validate_file() -> None:
    """It validates file correctly."""
    assert validate_file(FILE_SAMPLE, FILE_SCHEMA) is None


def test_validate_file_fail() -> None:
    """It validates file correctly."""
    xml = StringIO("<shiporder></shiporder>")
    errorExpected = (
        "<string>:1:0:ERROR:SCHEMASV:SCHEMAV_CVC_COMPLEX_TYPE_4: "
        "Element 'shiporder': The attribute 'orderid' is required but missing."
    )
    errorActual = validate_file(xml, FILE_SCHEMA)

    assert errorActual is not None
    assert str(errorActual[0]) == errorExpected
