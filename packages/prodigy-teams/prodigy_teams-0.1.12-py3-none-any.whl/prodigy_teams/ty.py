from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    NoReturn,
    Optional,
    Protocol,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)
from uuid import UUID

from pydantic import BaseModel
from radicli import ExistingDirPath, ExistingFilePath, StrOrUUID

# Union for scalar arg values, that can come form the CLI
AnyScalar = Union[str, bool, None, int, float, UUID]
JSONableDict = Dict[str, Any]


class BrokerStatusCheck(str, Enum):
    # Broker has not yet finished registration with PAM
    CREATING = "creating"
    # Address is not valid
    INVALID_ADDRESS = "invalid_address"
    # Could not connect to URL
    NOT_FOUND = "not_found"
    # Status request failed
    REQUEST_ERROR = "request_error"
    # Status response http error
    RESPONSE_ERROR = "response_error"
    # Status response indicates issues
    ISSUES = "issues"
    # Status response indicates no issues
    RUNNING = "running"

    def __str__(self) -> str:
        return self.value


_T = TypeVar("_T")


class _Page(Protocol[_T]):
    items: List[_T]
    total: int  # Count of the items across all pages
    page: int  # Matches the query param or default
    size: int  # Matches the query param or default


Page = TypeVar("Page", bound=_Page)


__all__ = [
    "Any",
    "AnyScalar",
    "BaseModel",
    "BrokerStatusCheck",
    "Callable",
    "cast",
    "datetime",
    "Dict",
    "Dict",
    "Enum",
    "ExistingDirPath",
    "ExistingFilePath",
    "Generator",
    "Generic",
    "IO",
    "Iterable",
    "Iterator",
    "JSONableDict",
    "List",
    "Literal",
    "NoReturn",
    "Optional",
    "overload",
    "Path",
    "Protocol",
    "Sequence",
    "Set",
    "StrOrUUID",
    "Tuple",
    "Type",
    "TypeVar",
    "Union",
    "UUID",
    "Page",
]
