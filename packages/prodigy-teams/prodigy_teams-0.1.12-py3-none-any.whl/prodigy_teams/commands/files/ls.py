from radicli import Arg
from wasabi import msg

from ... import ty
from ...auth import get_current_auth
from ...cli import cli
from ...config import SavedSettings
from ...messages import Messages
from ...prodigy_teams_broker_sdk import models as broker_models
from ...ui import print_as_json
from ...util import resolve_remote_path


@cli.subcommand(
    "files",
    "ls",
    remote=Arg(help=Messages.remote_path),
    recurse=Arg("--recurse", "-r", help=Messages.recurse_list),
    as_json=Arg("--json", help=Messages.as_json),
    cluster_host=Arg("--cluster-host", help=Messages.cluster_host),
)
def ls(
    remote: str,
    recurse: bool = False,
    as_json: bool = False,
    cluster_host: ty.Optional[str] = None,
) -> broker_models.PathList:
    """List the files under `remote`"""
    broker_host = SavedSettings.get_and_save("broker_host", cluster_host)
    auth = get_current_auth()
    path = resolve_remote_path(auth.client, remote, broker_host)
    body = broker_models.Listing(path=path, recurse=recurse, include_stats=False)
    files = auth.broker_client.files.list_dir(body)
    if as_json:
        print_as_json(files.dict())
    else:
        msg.info(remote)
        for file_path in files.paths:
            print(file_path)
    return files
