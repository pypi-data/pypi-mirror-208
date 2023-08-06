import json
from collections.abc import Iterator

from iteriotools import RawIterIO


def _json_document() -> Iterator[bytes]:
    yield b"{"
    yield b'"key"'
    yield b":"
    yield b'"value"'
    yield b"}"


def test_raw_iter_io():
    expected = {"key": "value"}
    actual = json.load(RawIterIO(_json_document()))
    assert actual == expected
