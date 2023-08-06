from radicli import Arg
from wasabi import msg

from .. import ty
from ..auth import get_current_auth
from ..cli import cli
from ..errors import CLIError, ProdigyTeamsErrors
from ..messages import Messages
from ..prodigy_teams_pam_sdk.models import BrokerPathReturning
from ..query import resolve_path, resolve_path_id
from ..ui import print_info_table, print_table_with_select
from ..util import resolve_remote_path


@cli.subcommand("paths", "list")
def list() -> ty.Sequence[BrokerPathReturning]:
    """List all cluster path aliases"""
    client = get_current_auth().client
    res = client.broker_path.all()
    print_table_with_select(res.items, select=["created", "id", "name", "path"])
    return res.items


@cli.subcommand(
    "paths",
    "info",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="path")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="path")),
    as_json=Arg("--json", help=Messages.as_json),
)
def info(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    as_json: bool = False,
) -> BrokerPathReturning:
    """Get detailed info for a path alias"""
    res = resolve_path(name_or_id, broker_id=cluster_id)
    print_info_table(res, as_json=as_json)
    return res


@cli.subcommand(
    "paths",
    "create",
    name=Arg(help=Messages.name.format(noun="path")),
    path=Arg(help=Messages.path.format(noun="cluster directory")),
    exists_ok=Arg("--exists-ok", help=Messages.exists_ok),
)
def create(name: str, path: str, exists_ok: bool = False) -> ty.Optional[ty.UUID]:
    """Create a new path alias"""
    auth = get_current_auth()
    client = auth.client
    broker_id = auth.broker_id
    path = resolve_remote_path(client, path, default_broker=auth.broker_host)
    try:
        res = client.broker_path.create(name=name, path=path, broker_id=broker_id)
    except ProdigyTeamsErrors.BrokerPathExists:
        if exists_ok:
            msg.info(Messages.T001.format(noun="path", name=name))
            return None
        raise CLIError(Messages.E002.format(noun="path", name=name))
    except ProdigyTeamsErrors.BrokerPathInvalid:
        raise CLIError(Messages.E004.format(noun="path", name=name))
    except ProdigyTeamsErrors.BrokerPathForbiddenCreate:
        raise CLIError(Messages.E003.format(noun="path", name=name))
    msg.divider("Path Alias")
    msg.table(res.dict())
    return res.id


@cli.subcommand(
    "paths",
    "delete",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="path")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="path")),
)
def delete(
    name_or_id: ty.StrOrUUID, cluster_id: ty.Optional[ty.UUID] = None
) -> ty.UUID:
    """Delete a path alias"""
    path_id = resolve_path_id(name_or_id, broker_id=cluster_id)
    auth = get_current_auth()
    try:
        auth.client.broker_path.delete(id=path_id)
    except (
        ProdigyTeamsErrors.ProjectForbiddenDelete,
        ProdigyTeamsErrors.ProjectNotFound,
    ):
        raise CLIError(Messages.E006.format(noun="path", name=name_or_id))
    else:
        msg.good(Messages.T003.format(noun="path", name=name_or_id))
    return path_id
