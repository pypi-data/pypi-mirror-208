from . import ty


class BrokerError(Exception):
    def __init__(
        self,
        message: ty.Optional[str] = None,
        detail: ty.Optional[str] = None,
        status: ty.Optional[int] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__()
        self.message = message
        self.detail = detail
        self.status = status
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        output = ""
        if self.message:
            output = self.message
        if self.detail:
            output += f"\n{self.detail}" if output else self.detail
        return output


class NotFound(BrokerError):
    pass


class Exists(BrokerError):
    pass


class ClientError(BrokerError):
    pass


class PT_MaintenanceMode(BrokerError):
    pass


class DatasetCreateFailed(BrokerError):
    pass


class DatasetExists(BrokerError):
    pass


class DatasetNotFound(BrokerError):
    pass


class PT_Package_Exists(BrokerError):
    pass


class PT_Package_NotFound(BrokerError):
    pass


class PackageNotWheel(BrokerError):
    pass


class EnvNotFound(BrokerError):
    pass


class JobMetaNotFound(BrokerError):
    pass


class FileError(BrokerError):
    pass


class SecretCreateFailed(BrokerError):
    pass


class SecretExists(BrokerError):
    pass


class SecretNotFound(BrokerError):
    pass


class AuthError(BrokerError):
    def __init__(self, detail: str = "Auth Error"):
        self.status = 401
        self.detail = detail

    def __str__(self):
        return self.detail
