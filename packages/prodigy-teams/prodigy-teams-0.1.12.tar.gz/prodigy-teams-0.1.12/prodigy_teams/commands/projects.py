from radicli import Arg
from wasabi import msg

from .. import ty
from ..auth import get_current_auth
from ..cli import cli
from ..errors import CLIError, ProdigyTeamsErrors
from ..messages import Messages
from ..prodigy_teams_pam_sdk.models import ProjectCreating, ProjectReturning
from ..query import resolve_project, resolve_project_id
from ..ui import print_info_table, print_table_with_select


@cli.subcommand(
    "projects",
    "list",
    # fmt: off
    select=Arg("--select", help=Messages.select.format(opts=list(ProjectReturning.__fields__))),
    name=Arg("--name", help=Messages.filter_by.format(filter="name")),
    # fmt: on
)
def list(
    select: ty.List[str] = ["id", "name"], name: ty.Optional[str] = None
) -> ty.Sequence[ProjectReturning]:
    """List all projects"""
    client = get_current_auth().client
    res = client.project.all(name=name)
    print_table_with_select(res.items, select=select)
    return res.items


@cli.subcommand(
    "projects",
    "info",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="project")),
    as_json=Arg("--json", help=Messages.as_json),
)
def info(name_or_id: ty.StrOrUUID, as_json: bool = False) -> ProjectReturning:
    """Get detailed info for a project"""
    res = resolve_project(name_or_id)
    print_info_table(res, as_json=as_json)
    return res


@cli.subcommand(
    "projects",
    "create",
    name=Arg(help=Messages.name.format(noun="project")),
    description=Arg(help=Messages.description.format(noun="project")),
    exists_ok=Arg("--exists-ok", help=Messages.exists_ok),
)
def create(
    name: str, description: str, exists_ok: bool = False
) -> ty.Optional[ty.UUID]:
    """Create a new project"""
    auth = get_current_auth()
    client = auth.client
    body = ProjectCreating(name=name, description=description)
    try:
        res = client.project.create(body)
    except ProdigyTeamsErrors.ProjectExists:
        if exists_ok:
            msg.info(Messages.T001.format(noun="project", name=name))
            return None
        raise CLIError(Messages.E002.format(noun="project", name=name))
    except ProdigyTeamsErrors.ProjectInvalid:
        raise CLIError(Messages.E004.format(noun="project", name=name))
    msg.divider("Project")
    msg.table(res.dict())
    return res.id


@cli.subcommand(
    "projects",
    "delete",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="project")),
)
def delete(name_or_id: ty.StrOrUUID) -> ty.UUID:
    """Delete a project"""
    project_id = resolve_project_id(name_or_id)
    auth = get_current_auth()
    try:
        auth.client.project.delete(id=project_id)
    except (
        ProdigyTeamsErrors.ProjectForbiddenDelete,
        ProdigyTeamsErrors.ProjectNotFound,
    ):
        raise CLIError(Messages.E006.format(noun="project", name=name_or_id))
    else:
        msg.good(Messages.T003.format(noun="project", name=name_or_id))
    return project_id
