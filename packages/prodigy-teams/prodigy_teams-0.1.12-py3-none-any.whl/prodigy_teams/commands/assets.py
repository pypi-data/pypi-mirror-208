import json

from radicli.util import Arg
from wasabi import msg

from .. import ty
from ..auth import get_current_auth
from ..cli import cli
from ..errors import CLIError, ProdigyTeamsErrors
from ..messages import Messages
from ..prodigy_teams_pam_sdk.models import AssetCreating, AssetReturning
from ..query import resolve_asset, resolve_asset_id
from ..ui import print_info_table, print_table_with_select
from ..util import resolve_remote_path


@cli.subcommand(
    "assets",
    "list",
    # fmt: off
    select=Arg("--select", help=Messages.select.format(opts=list(AssetReturning.__fields__))),
    # fmt: on
)
def list(select: ty.List[str] = ["id", "name", "kind"]) -> ty.Sequence[AssetReturning]:
    """List all assets on the cluster registered with Prodigy Teams"""
    client = get_current_auth().client
    res = client.asset.all()
    print_table_with_select(res.items, select=select)
    return res.items


@cli.subcommand(
    "assets",
    "info",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="asset")),
    project_id=Arg(help=Messages.project_id.format(noun="action")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="action")),
    as_json=Arg("--json", help=Messages.as_json),
)
def info(
    name_or_id: ty.StrOrUUID,
    project_id: ty.Optional[ty.UUID] = None,
    cluster_id: ty.Optional[ty.UUID] = None,
    as_json: bool = False,
) -> AssetReturning:
    """
    Get detailed info for an asset uploaded to the cluster and registered
    with Prodigy Teams
    """
    res = resolve_asset(name_or_id, broker_id=cluster_id, project_id=project_id)
    print_info_table(res, as_json=as_json)
    return res


@cli.subcommand(
    "assets",
    "create",
    name=Arg(help=Messages.name.format(noun="asset")),
    kind=Arg("--kind", help=Messages.asset_kind),
    path=Arg(help=Messages.path.format(noun="asset")),
    version=Arg("--version", help=Messages.version.format(noun="asset")),
    meta=Arg("--meta", help=Messages.asset_meta),
    exists_ok=Arg("--exists-ok", help=Messages.exists_ok),
)
def create(
    kind: str,
    name: str,
    path: str,
    version: str = "0.0.0",
    meta: str = "{}",
    exists_ok: bool = False,
) -> ty.Optional[ty.UUID]:
    """
    Create an asset on the cluster and register it with Prodigy Teams. Assets
    point to files or directories you control. The Prodigy Teams server only has
    a reference to them. This command doesn't transfer any data. See `ptc files`
    for utilities to transfer files to and from your cluster
    """
    try:
        _ = json.loads(meta)
    except ValueError:
        raise CLIError(Messages.E121, str(meta))
    auth = get_current_auth()
    client = auth.client
    resolved_path = resolve_remote_path(client, path, auth.broker_host)
    try:
        asset = client.asset.create(
            AssetCreating(
                broker_id=auth.broker_id,
                name=name,
                kind=kind,
                version=version,
                meta=json.loads(meta),
                path=resolved_path,
            )
        )
    except ProdigyTeamsErrors.AssetExists:
        if exists_ok:
            msg.info(Messages.T001.format(noun="asset", name=name))
            return None
        raise CLIError(Messages.E002.format(noun="asset", name=name))
    assert asset.path is not None
    msg.good(Messages.T002.format(noun="asset", name=asset.name), resolved_path)
    return asset.id


@cli.subcommand(
    "assets",
    "delete",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="asset")),
    project_id=Arg(help=Messages.project_id.format(noun="asset")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="asset")),
)
def delete(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    project_id: ty.Optional[ty.UUID] = None,
) -> ty.UUID:
    """Delete an asset registered with Prodigy Teams"""
    asset_id = resolve_asset_id(name_or_id, broker_id=cluster_id, project_id=project_id)
    auth = get_current_auth()
    try:
        auth.client.asset.delete(id=asset_id)
    except ProdigyTeamsErrors.AssetNotFound:
        raise CLIError(Messages.E006.format(noun="asset", name=name_or_id))
    except ProdigyTeamsErrors.AssetForbiddenDelete:
        raise CLIError(Messages.E007.format(noun="asset", name=name_or_id))
    else:
        msg.good(Messages.T003.format(noun="asset", name=name_or_id))
    return asset_id
