import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generator,
    Generic,
    Iterator,
    List,
    Literal,
    NamedTuple,
    NoReturn,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from pydantic import BaseModel, ConstrainedStr, Field, conint, constr
from pydantic.generics import GenericModel


class NotificationTypes(str, Enum):
    """Types of notifications.

    Should match the values in app/util/constants.ts"""

    invite_accept = "INVITE_ACCEPT"
    system = "SYSTEM"
    goal = "GOAL"


T = TypeVar("T")


class Page(GenericModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: conint(ge=1)  # type: ignore
    size: conint(ge=1)  # type: ignore


class Fields:
    str255: str = Field(..., max_length=255)
    maybe_str255: Optional[str] = Field(None, lt=255)


SEMVER_PATTERN = re.compile(
    r"^((([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)$"  # noqa
)


class SemverStr(ConstrainedStr):
    regex = SEMVER_PATTERN


FuncT = TypeVar("FuncT", bound=Callable)
Wrapper = Callable[[FuncT], FuncT]
Decorator = Callable[[Any, Any], Wrapper]


__all__ = [
    "Any",
    "Callable",
    "Union",
    "List",
    "Dict",
    "NoReturn",
    "Optional",
    "Wrapper",
    "Decorator",
    "Sequence",
    "cast",
    "Iterator",
    "Set",
    "Tuple",
    "Type",
    "TypeVar",
    "Generic",
    "ClassVar",
    "Path",
    "Generator",
    "datetime",
    "constr",
    "Fields",
    "BaseModel",
    "ModuleType",
    "UUID",
    "Literal",
    "NamedTuple",
]
