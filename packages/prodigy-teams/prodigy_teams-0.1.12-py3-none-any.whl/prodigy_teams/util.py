import os
import re
import sys
from dataclasses import dataclass
from urllib.parse import urlparse
from uuid import UUID

from . import ty
from .messages import Messages
from .prodigy_teams_pam_sdk import Client
from .prodigy_teams_pam_sdk.models import BrokerPathReading

APP_NAME = "prodigy-teams"
CYGWIN = sys.platform.startswith("cygwin")
MSYS2 = sys.platform.startswith("win") and ("GCC" in sys.version)
# Determine local App Engine environment, per Google's own suggestion
APP_ENGINE = "APPENGINE_RUNTIME" in os.environ and "Development/" in os.environ.get(
    "SERVER_SOFTWARE", ""
)
WIN = sys.platform.startswith("win") and not APP_ENGINE and not MSYS2


@dataclass(frozen=True)
class URL:
    # e.g. https://pam.explosion.rocks:8080/path
    url: str
    # e.g. pam.explosion.rocks:8080
    netloc: str
    # e.g. 8080, defaults to 80 for http and 443 for https
    port: int
    # e.g. https
    scheme: str

    @classmethod
    def parse(cls, host_or_url: str, scheme="https") -> "URL":
        host_or_url = host_or_url.strip().strip("/")
        if not host_or_url.startswith("http"):
            host_or_url = f"{scheme}://{host_or_url}"
        parse = urlparse(host_or_url)
        netloc = parse.netloc
        url = parse.geturl()
        scheme = parse.scheme
        port = (
            parse.port
            if parse.port is not None
            else cls._default_port_from_scheme(scheme)
        )
        return cls(url=url, netloc=netloc, port=port, scheme=scheme)

    @classmethod
    def _default_port_from_scheme(cls, scheme: str) -> int:
        if scheme == "https":
            return 443
        elif scheme == "http":
            return 80
        else:
            raise ValueError(f"unsupported url scheme: {scheme}")

    def __format__(self, __format_spec: str) -> str:
        return self.url

    def __str__(self) -> str:
        return self.url

    def __truediv__(self, sub_path: str) -> "URL":
        return URL(
            url=f"{self.url}/{sub_path.strip('/')}",
            netloc=self.netloc,
            port=self.port,
            scheme=self.scheme,
        )


# Source: https://github.com/pallets/click/blob/cba52fa76135af2edf46c154203b47106f898eb3/src/click/utils.py#L408
def get_app_dir(app_name: str, roaming: bool = True, force_posix: bool = False) -> str:
    """
    Returns the config folder for the application.  The default behavior
    is to return whatever is most appropriate for the operating system.
    """

    def _posixify(name: str) -> str:
        return "-".join(name.split()).lower()

    if WIN:
        key = "APPDATA" if roaming else "LOCALAPPDATA"
        folder = os.environ.get(key)
        if folder is None:
            folder = os.path.expanduser("~")
        return os.path.join(folder, app_name)
    if force_posix:
        return os.path.join(os.path.expanduser(f"~/.{_posixify(app_name)}"))
    if sys.platform == "darwin":
        return os.path.join(
            os.path.expanduser("~/Library/Application Support"), app_name
        )
    return os.path.join(
        os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
        _posixify(app_name),
    )


def is_local(path_str: str) -> bool:
    if path_str.startswith("{"):
        return False
    elif path_str.startswith("s3://"):
        return False
    elif path_str.startswith("gs://"):
        return False
    else:
        return True


def resolve_remote_path(client: Client, remote: str, default_broker: str) -> str:
    path_parts = parse_remote_path(remote)
    if path_parts[1] is None:
        return path_parts[2]
    broker_name, path_name, subpath = path_parts
    broker_name = broker_name or default_broker
    query = BrokerPathReading(
        broker_id=_resolve_broker_ref(client, broker_name),
        name=path_name,
        id=None,
        path=None,
    )
    result = client.broker_path.read(query)
    return os.path.join(result.path, subpath)


# Place this close to the function for convenience.
# TODO: This will have trouble with escaped curlies right?
_PATH_RE = re.compile(r"^(?:\{(\w+)\}:)?(?:\{(\w+)\}/?)?([^{}]*)$")


def parse_remote_path(path: str) -> ty.Tuple[ty.Optional[str], ty.Optional[str], str]:
    match_obj = _PATH_RE.match(path)
    if match_obj is None:
        raise ValueError(Messages.E128.format(path=path))
    groups = match_obj.groups()
    if len(groups) != 3:
        raise ValueError(Messages.E128.format(path=path))
    return groups


def _resolve_broker_ref(client: Client, name_or_id: str) -> ty.UUID:
    """
    Resolve reference to a task by name or ID. If an ID is given, return it.
    If it's a name, look up the ID.
    """
    try:
        return UUID(name_or_id)
    except ValueError:
        pass
    task = client.broker.read(name=name_or_id)
    return task.id
