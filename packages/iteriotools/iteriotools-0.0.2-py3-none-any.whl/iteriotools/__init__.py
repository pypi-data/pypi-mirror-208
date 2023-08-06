# SPDX-License-Identifier: MIT

from collections.abc import Generator, Iterable
from io import RawIOBase


def inbuffered(iterable: Iterable[bytes]) -> Generator[bytes, int, None]:
    size = yield b""
    for data in iterable:
        while data:
            chunk, data = data[:size], data[size:]
            size = yield chunk


class RawIterIO(RawIOBase):
    def __init__(self, data: Iterable[bytes], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = inbuffered(data)
        next(self._data)

    def readinto(self, b, /) -> int:
        try:
            data = self._data.send(len(b))
        except StopIteration:
            return 0

        b[: len(data)] = data
        return len(data)

    def readable(self) -> bool:
        return True
