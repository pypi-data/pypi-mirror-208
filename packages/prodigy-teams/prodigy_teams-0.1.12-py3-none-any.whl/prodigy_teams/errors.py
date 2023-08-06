from httpx import (
    ConnectError,
    ConnectTimeout,
    HTTPError,
    HTTPStatusError,
    InvalidURL,
    ReadTimeout,
    RequestError,
)

from . import ty
from .messages import Messages
from .prodigy_teams_broker_sdk.errors import BrokerError
from .prodigy_teams_pam_sdk import errors as ProdigyTeamsErrors

HTTPXErrors = (
    ConnectError,
    ConnectTimeout,
    HTTPError,
    HTTPStatusError,
    InvalidURL,
    RequestError,
    ReadTimeout,
)


class ProdigyTeamsError(Exception):
    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(self.message)


class ProdigyTeamsIDTokenError(ProdigyTeamsError):
    pass


class CLIError(Exception):
    def __init__(self, title: str, text: ty.Optional[ty.Any] = None) -> None:
        self.title = title
        self.text = text
        self.message = self.title + (f"\n{self.text}" if self.text else "")
        super().__init__(self.message)


class ProdigyTeamsParseSecretsError(ProdigyTeamsError):
    def __init__(
        self, secrets_file: ty.Optional[ty.Path], error: ty.Optional[Exception] = None
    ) -> None:
        path_details = (
            f" (`{str(secrets_file.absolute())}`)" if secrets_file is not None else ""
        )
        error_details = f"\n\n{str(error)}" if error is not None else ""
        self.message = Messages.E045.format(
            path_details=path_details, error_details=error_details
        )

    def __str__(self) -> str:
        return self.message


__all__ = [
    "CLIError",
    "ConnectError",
    "ConnectTimeout",
    "HTTPError",
    "HTTPStatusError",
    "HTTPXErrors",
    "InvalidURL",
    "ProdigyTeamsError",
    "ProdigyTeamsErrors",
    "ProdigyTeamsIDTokenError",
    "ProdigyTeamsParseSecretsError",
    "RequestError",
    "BrokerError",
]
