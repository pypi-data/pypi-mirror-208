import json
from pathlib import Path

from radicli import Radicli, get_list_converter
from wasabi import msg

from . import about, ty
from .errors import CLIError, HTTPError, HTTPXErrors, ProdigyTeamsError
from .messages import Messages
from .prodigy_teams_broker_sdk.errors import BrokerError
from .prodigy_teams_pam_sdk.errors import AuthError, RecipeProcessingError

HELP = """Prodigy Teams Command Line Interface.
More info at https://github.com/explosion/prodigy-teams/tree/main/cli"""


def handle_cli_error(err: ty.Union[CLIError, RecipeProcessingError]) -> int:
    msg.fail(str(err.title), str(err.text) if err.text else "")
    return 1


def handle_teams_error(err: ProdigyTeamsError) -> int:
    msg.fail(str(err.message))
    return 1


def handle_broker_error(err: BrokerError) -> int:
    err_type = "Unexpected error"
    err_message = None
    if err.detail is not None:
        try:
            detail = json.loads(err.detail)
            err_type = detail["type"]
            err_message = detail["message"]
        except Exception:
            pass
    text = Messages.E046.format(type=err_type)
    msg.fail(text, err_message)
    return 1


def handle_http_error(err: HTTPError) -> int:
    # This happens for all other request errors we're not catching
    if hasattr(err, "response"):
        try:
            detail = json.loads(err.response.text)  # type: ignore
            message = ", ".join(str(d) for d in detail["detail"])
        except Exception:
            message = str(err)
        status_code = err.response.status_code  # type: ignore
        msg.fail(Messages.E047 + f" ({status_code})", message)
    else:
        msg.fail(Messages.E047, err)
    return 1


def handle_auth_error(err: AuthError) -> int:
    msg.fail(
        Messages.E039.format(message=err.message),
        Messages.E040.format(command=f"{about.__prog__} login"),
    )
    return 1


# Custom types mapped to how they should be converted on the CLI
CONVERTERS = {ty.List[str]: get_list_converter(str)}
# Custom error types mapped to how they should be handled
ERRORS = {
    CLIError: handle_cli_error,
    RecipeProcessingError: handle_cli_error,
    ProdigyTeamsError: handle_teams_error,
    BrokerError: handle_broker_error,
    **{error: handle_http_error for error in HTTPXErrors},
}


cli = Radicli(
    prog=about.__prog__,
    help=HELP,
    version=about.__version__,
    converters=CONVERTERS,
    errors=ERRORS,
)
cli.placeholder("actions", description=Messages.doc_actions)
cli.placeholder("assets", description=Messages.doc_assets)
cli.placeholder("clusters", description=Messages.doc_clusters)
cli.placeholder("config", description=Messages.doc_config)
cli.placeholder("consul", description=Messages.doc_consul)
cli.placeholder("datasets", description=Messages.doc_datasets)
cli.placeholder("files", description=Messages.doc_files)
cli.placeholder("packages", description=Messages.doc_packages)
cli.placeholder("paths", description=Messages.doc_paths)
cli.placeholder("projects", description=Messages.doc_projects)
cli.placeholder("recipes", description=Messages.doc_recipes)
cli.placeholder("secrets", description=Messages.doc_secrets)
cli.placeholder("tasks", description=Messages.doc_tasks)
cli.placeholder("team", description=Messages.doc_team)


def document_cli(cli: Radicli, *, root: Path = Path.cwd()) -> str:
    """Auto-generate Markdown API docs for ptc CLI"""
    title = "Prodigy Teams CLI"
    desc = (
        f"Before using Prodigy Teams CLI you need to have a **Prodigy Teams** "
        f"account. You also need a deployed cluster and Python 3.6+. To "
        f"see all available commands or subcommands, you can use the `--help` "
        f"flag, e.g. `{cli.prog} --help`."
    )
    return cli.document(title=title, description=desc, path_root=root)
