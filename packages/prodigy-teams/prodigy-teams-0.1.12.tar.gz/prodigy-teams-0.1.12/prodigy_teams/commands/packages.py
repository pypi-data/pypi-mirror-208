from radicli import Arg
from wasabi import msg

from .. import ty
from ..auth import get_current_auth
from ..cli import cli
from ..errors import CLIError, ProdigyTeamsErrors
from ..messages import Messages
from ..prodigy_teams_pam_sdk.models import PackageReturning
from ..query import resolve_package
from ..ui import print_info_table, print_table_with_select


@cli.subcommand("packages", "list")
def list() -> ty.Sequence[PackageReturning]:
    """List all packages"""
    client = get_current_auth().client
    res = client.package.all_readable()

    packages = [
        {
            **package.dict(),
            "used by": package.tasks_using + package.actions_using
            if package.tasks_using is not None and package.actions_using is not None
            else "-",
            "tasks using": package.tasks_using
            if package.tasks_using is not None
            else "-",
            "actions using": package.actions_using
            if package.actions_using is not None
            else "-",
        }
        for package in res.items
    ]
    print_table_with_select(
        packages,
        select=["id", "name", "version", "used by", "tasks using", "actions using"],
    )
    return res.items


@cli.subcommand(
    "packages",
    "info",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="package")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="package")),
    as_json=Arg("--json", help=Messages.as_json),
)
def info(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    as_json: bool = False,
) -> PackageReturning:
    """Get detailed info for a package"""
    auth = get_current_auth()
    if cluster_id is None:
        cluster_id = auth.broker_id
    res = resolve_package(name_or_id, broker_id=cluster_id)
    print_info_table(res, as_json=as_json)
    return res


@cli.subcommand(
    "packages",
    "create",
    name=Arg(help=Messages.name.format(noun="package")),
    kind=Arg("--kind", help=Messages.kind.format(noun="package")),
    exists_ok=Arg("--exists-ok", help=Messages.exists_ok),
)
def create(name: str, kind: str, exists_ok: bool = False) -> ty.Optional[ty.UUID]:
    """Create a new package"""
    auth = get_current_auth()
    client = auth.client
    broker_id = auth.broker_id
    try:
        res = client.package.create(name=name, kind=kind, broker_id=broker_id)
    except ProdigyTeamsErrors.PackageExists:
        if exists_ok:
            msg.info(Messages.T001.format(noun="package", name=name))
            return None
        raise CLIError(Messages.E002.format(noun="package", name=name))
    except ProdigyTeamsErrors.PackageInvalid:
        raise CLIError(Messages.E004.format(noun="package", name=name))
    except ProdigyTeamsErrors.PackageForbiddenCreate:
        raise CLIError(Messages.E003.format(noun="package", name=name))
    msg.divider("Package")
    msg.table(res)
    return res.id


@cli.subcommand(
    "packages",
    "delete",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="package")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="package")),
    force=Arg("--force", help="Delete related actions or tasks as well"),
)
def delete(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    force: bool = False,
) -> ty.UUID:
    """Delete a package"""
    auth = get_current_auth()
    if cluster_id is None:
        cluster_id = auth.broker_id
    package = resolve_package(name_or_id, broker_id=cluster_id)
    package_id = package.id
    try:
        auth.client.package.delete(id=package_id, force=force)
    except (ProdigyTeamsErrors.PackageForbiddenDeleteForExistingPlans):
        raise CLIError(
            Messages.E048.format(
                noun="package",
                name=name_or_id,
                others="other actions or tasks",
                flag="--force",
            )
        )
    except (
        ProdigyTeamsErrors.PackageForbiddenDelete,
        ProdigyTeamsErrors.PackageNotFound,
    ):
        raise CLIError(Messages.E006.format(noun="package", name=name_or_id))
    else:
        msg.good(Messages.T003.format(noun="package", name=name_or_id))
    return package_id
