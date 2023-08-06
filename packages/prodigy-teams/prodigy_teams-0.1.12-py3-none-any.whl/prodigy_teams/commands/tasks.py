import sys

from radicli import Arg
from wasabi import msg

from .. import ty
from ..auth import get_current_auth
from ..cli import cli
from ..errors import BrokerError, CLIError, HTTPXErrors, ProdigyTeamsError
from ..messages import Messages
from ..prodigy_teams_broker_sdk.models import JobLogRequest
from ..prodigy_teams_pam_sdk.models import TaskReturning
from ..query import delete_job, resolve_recipe, resolve_task, start_job, stop_job
from ..ui import (
    print_args_table,
    print_info_table,
    print_logs,
    print_recipes_help,
    print_table_with_select,
)
from ._recipe_subcommand import create_from_recipe, request_recipes


@cli.subcommand_with_extra(
    "tasks",
    "create",
    exists_ok=Arg("--exists-ok", help=Messages.exists_ok),
    no_start=Arg("--no-start", help=Messages.no_start),
    _show_help=Arg("--help", "-h", help=Messages.help),
)
def create(
    exists_ok: bool = False,
    no_start: bool = False,
    _show_help: bool = False,
    _extra: ty.List[str] = [],
) -> ty.UUID:
    """
    Create a new action. The available action recipes are fetched from your
    cluster and are added as dynamic subcommands. You can see more details
    and available arguments by calling the subcommand with --help, e.g. create
    [name] --help
    """
    # TODO: We should just get one recipe here, rather than all of them. That
    # will also save us from having to query for all the objects.
    auth = get_current_auth()
    try:
        schemas = request_recipes(auth=auth, is_action=False)
    except ProdigyTeamsError as e:
        raise CLIError(Messages.E009, e)
    except HTTPXErrors as e:
        raise CLIError(Messages.E009, e)
    if not _extra:
        print_recipes_help(schemas, "Create a new task", "tasks create")
        sys.exit(0)
    args = [*_extra]
    name = args.pop(0)
    if name not in schemas:
        opts = f"Available: {', '.join(schemas.keys())}"
        raise CLIError(Messages.E010.format(noun="task", name=name), opts)
    schema = resolve_recipe(name, broker_id=auth.broker_id)
    task_id, plan = create_from_recipe(
        schema, args, command="tasks", show_help=_show_help, exists_ok=exists_ok
    )
    msg.good(Messages.T002.format(noun="task", name=task_id))
    print_args_table(plan.args, schema.form_schema.cli_names)
    if not no_start:
        start(task_id)
    return task_id


@cli.subcommand(
    "tasks",
    "list",
    # fmt: off
    select=Arg("--select", help=Messages.select.format(opts=list(TaskReturning.__fields__))),
    # fmt: on
)
def list(select: ty.List[str] = ["id", "name", "state"]) -> ty.Sequence[TaskReturning]:
    """
    List the tasks on the cluster. By default, this includes their ID, name
    and current state, e.g. created or completed
    """
    client = get_current_auth().client
    res = client.task.all(page=1, size=100)
    print_table_with_select(res.items, select=select)
    return res.items


@cli.subcommand(
    "tasks",
    "info",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="task")),
    project_id=Arg(help=Messages.project_id.format(noun="task")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="task")),
    as_json=Arg("--json", help=Messages.as_json),
)
def info(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    project_id: ty.Optional[ty.UUID] = None,
    as_json: bool = False,
) -> TaskReturning:
    """Print information about a task on the cluster"""
    res = resolve_task(name_or_id, broker_id=cluster_id, project_id=project_id)
    print_info_table(res, exclude=["plan"], as_json=as_json)
    return res


@cli.subcommand(
    "tasks",
    "logs",
    name_or_id=Arg(help=Messages.name_or_id_optional.format(noun="tasks")),
    project_id=Arg(help=Messages.project_id.format(noun="tasks")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="tasks")),
    as_json=Arg("--json", help=Messages.as_json),
)
def logs(
    name_or_id: ty.Optional[ty.StrOrUUID] = None,
    project_id: ty.Optional[ty.UUID] = None,
    cluster_id: ty.Optional[ty.UUID] = None,
    as_json: bool = False,
) -> ty.Optional[str]:
    """Get logs for a task on the cluster"""
    job = resolve_task(name_or_id, broker_id=cluster_id, project_id=project_id)
    auth = get_current_auth()
    try:
        res = auth.broker_client.jobs.logs(JobLogRequest(id=job.id))
    except BrokerError as e:
        raise CLIError(Messages.E011.format(noun="task"), e)
    text = res.text if res is not None else None
    print_logs(text, as_json=as_json)
    return text


@cli.subcommand(
    "tasks",
    "start",
    name_or_id=Arg(help=Messages.name_or_id_optional.format(noun="task")),
    project_id=Arg(help=Messages.project_id.format(noun="task")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="task")),
)
def start(
    name_or_id: ty.Optional[ty.StrOrUUID] = None,
    project_id: ty.Optional[ty.UUID] = None,
    cluster_id: ty.Optional[ty.UUID] = None,
) -> ty.UUID:
    """Start a task on the cluster"""
    job = resolve_task(name_or_id, broker_id=cluster_id, project_id=project_id)
    start_job(job, get_current_auth())
    return job.id


@cli.subcommand(
    "tasks",
    "stop",
    name_or_id=Arg(help=Messages.name_or_id_optional.format(noun="task")),
    project_id=Arg(help=Messages.project_id.format(noun="task")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="task")),
)
def stop(
    name_or_id: ty.Optional[ty.StrOrUUID] = None,
    project_id: ty.Optional[ty.UUID] = None,
    cluster_id: ty.Optional[ty.UUID] = None,
) -> ty.UUID:
    """Stop a task on the cluster"""
    job = resolve_task(name_or_id, broker_id=cluster_id, project_id=project_id)
    stop_job(job, get_current_auth())
    return job.id


@cli.subcommand(
    "tasks",
    "delete",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="task")),
    project_id=Arg(help=Messages.project_id.format(noun="task")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="task")),
)
def delete(
    name_or_id: ty.StrOrUUID,
    project_id: ty.Optional[ty.UUID] = None,
    cluster_id: ty.Optional[ty.UUID] = None,
) -> ty.UUID:
    """Delete a task by name or ID"""
    job = resolve_task(name_or_id, broker_id=cluster_id, project_id=project_id)
    delete_job(job, get_current_auth())
    return job.id
