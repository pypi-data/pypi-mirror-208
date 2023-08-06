from collections.abc import Generator, Iterator
from itertools import cycle

from hypothesis import given
from hypothesis.strategies import binary, integers, lists

from iteriotools import inbuffered


def test_inbuffer_is_a_generator():
    assert isinstance(inbuffered(()), Generator)


def test_inbuffer_first_elemet_is_always_empty():
    assert next(inbuffered(())) == b""


@given(data=lists(binary()), chunk_sizes=lists(integers(min_value=1), min_size=1))
def test_inbuffer_hypothesis(data: list[bytes], chunk_sizes: list[int]):
    inbuffer = inbuffered(data)
    next(inbuffer)

    def collector() -> Iterator[bytes]:
        sizes = cycle(chunk_sizes)
        while True:
            size = next(sizes)
            try:
                yield inbuffer.send(size)[:size]
            except StopIteration:
                return

    assert b"".join(data) == b"".join(collector())
