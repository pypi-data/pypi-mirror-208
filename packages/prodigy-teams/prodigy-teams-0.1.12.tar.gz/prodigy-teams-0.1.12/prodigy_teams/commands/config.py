from radicli import Arg
from wasabi import msg

from .. import ty
from ..cli import cli
from ..config import SavedSettings, config_dir
from ..messages import Messages
from ..query import resolve_action_id, resolve_project_id, resolve_task_id
from ..util import URL


@cli.subcommand("config", "reset")
def reset() -> None:
    """Reset all caching and configuration."""
    queue = list(config_dir().iterdir())
    for subpath in queue:
        if subpath.is_dir():
            queue.extend(list(subpath.iterdir()))
        else:
            msg.info(Messages.T021.format(subpath=subpath))
            subpath.unlink()


@cli.subcommand(
    "config",
    "project",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="project")),
)
def project(name_or_id: ty.StrOrUUID) -> ty.UUID:
    """Set the default project."""
    project_id = resolve_project_id(name_or_id)
    SavedSettings.get_and_save("project", project_id)
    msg.good(Messages.T019.format(noun="project", name=project_id))
    return project_id


@cli.subcommand(
    "config",
    "task",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="task")),
    project_id=Arg(help=Messages.project_id.format(noun="task")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="task")),
)
def task(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    project_id: ty.Optional[ty.UUID] = None,
) -> ty.UUID:
    """Set the default task."""
    task_id = resolve_task_id(name_or_id, project_id=project_id, broker_id=cluster_id)
    SavedSettings.get_and_save("task", task_id)
    msg.good(Messages.T019.format(noun="task", name=task_id))
    return task_id


@cli.subcommand(
    "config",
    "action",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="action")),
    project_id=Arg(help=Messages.project_id.format(noun="action")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="action")),
)
def action(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    project_id: ty.Optional[ty.UUID] = None,
) -> ty.UUID:
    """Set the default action."""
    action_id = resolve_action_id(
        name_or_id, project_id=project_id, broker_id=cluster_id
    )
    SavedSettings.get_and_save("action", action_id)
    msg.good(Messages.T019.format(noun="action", name=action_id))
    return action_id


@cli.subcommand(
    "config",
    "set-cluster-host",
    host=Arg(help=Messages.cluster_host_config),
)
def set_broker_host(host: str) -> None:
    """Set the broker cluster host."""
    host_url = URL.parse(host)
    SavedSettings.get_and_save("broker_host", str(host_url))
    msg.good(Messages.T019.format(noun="cluster host", name=host))


@cli.subcommand(
    "config",
    "set-pam-host",
    host=Arg(help=Messages.pam_host_config),
)
def set_pam_host(host: str) -> None:
    """Set the PAM host."""
    host_url = URL.parse(host)
    SavedSettings.get_and_save("pam_host", str(host_url))
    msg.good(Messages.T019.format(noun="PAM host", name=host))
