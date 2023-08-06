from radicli import Arg

from ... import ty
from ...auth import get_current_auth
from ...cli import cli
from ...config import SavedSettings
from ...errors import BrokerError, CLIError
from ...messages import Messages
from ...prodigy_teams_broker_sdk import models as broker_models
from ...util import resolve_remote_path


@cli.subcommand(
    "files",
    "rm",
    remote_path=Arg(help=Messages.remote_path),
    cluster_host=Arg("--cluster-host", help=Messages.cluster_host),
    missing_ok=Arg("--missing-ok", help=Messages.missing_ok),
)
def rm(
    remote_path: str, cluster_host: ty.Optional[str] = None, missing_ok: bool = False
) -> None:
    """Remove files from the cluster"""
    broker_host = SavedSettings.get_and_save("broker_host", cluster_host)
    auth = get_current_auth()
    path = resolve_remote_path(auth.client, remote_path, broker_host)
    body = broker_models.Deleting(path=path, missing_ok=missing_ok)
    try:
        auth.broker_client.files.delete(body)
    except BrokerError as e:
        raise CLIError(Messages.E017.format(verb="delete"), e)
