from typing import (
    IO,
    Any,
    Dict,
    Generic,
    List,
    Literal,
    NamedTuple,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from pydantic import BaseModel, conint
from pydantic.generics import GenericModel

T = TypeVar("T")


class Page(GenericModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: conint(ge=1)  # type: ignore
    size: conint(ge=1)  # type: ignore


__all__ = [
    "Any",
    "BaseModel",
    "cast",
    "Dict",
    "IO",
    "List",
    "Literal",
    "NamedTuple",
    "Optional",
    "Type",
    "Union",
    "UUID",
]
