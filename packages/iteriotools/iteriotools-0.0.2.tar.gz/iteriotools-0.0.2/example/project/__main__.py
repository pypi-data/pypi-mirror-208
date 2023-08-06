import json
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from functools import cache
from io import BufferedReader
from typing import Annotated, Protocol, Union
from uuid import uuid4

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic.json import pydantic_encoder

from iteriotools import RawIterIO

from .models import User
from .store import Store

app = FastAPI()


@app.get("/health")
async def health() -> None:
    pass


@cache
def _store() -> Store:
    return Store(users=(User(uuid4()) for _ in range(1 << 20)))


@app.get("/users/batched")
async def users_batch(store: Annotated[Store, Depends(_store)]) -> list[User]:
    return list(store.users)


@dataclass
class DataClass(Protocol):
    pass


_JSONScalar = Union[int, float, str]
_JSONSequence = Sequence["_JSON"]
_JSONMapping = Mapping[str, "_JSON"]
_JSONPydanticExtensions = Union[Enum, DataClass, BaseModel]
_JSON = Union[_JSONPydanticExtensions, _JSONMapping, _JSONSequence, _JSONScalar]


def _json_iter(obj: _JSON) -> Iterator[bytes]:
    if isinstance(obj, Mapping):
        yield b"{"
        for key, value in obj.items():
            if not isinstance(key, str):
                raise TypeError(f"Mapping keys must be strings, not: {type(key)=}")
            yield key.encode()
            yield b":"
            yield from _json_iter(value)
        yield b"}"
    elif isinstance(obj, Sequence):
        yield b"["
        for item in obj:
            yield from _json_iter(item)
        yield b"]"
    else:
        # XXX: may need to be refined if you have large models
        yield json.dumps(obj, default=pydantic_encoder).encode()


@app.get("/users/streamed", response_class=StreamingResponse)
async def users(store: Annotated[Store, Depends(_store)]) -> StreamingResponse:
    return StreamingResponse(content=BufferedReader(RawIterIO(_json_iter(store.users))), media_type="application/json")
