import sys

from radicli import (
    DEFAULT_PLACEHOLDER,
    Arg,
    ArgparseArg,
    ArgumentParser,
    ConverterType,
    get_arg,
)
from wasabi import msg

from .. import ty
from ..auth import CLIAuth, get_current_auth
from ..cli import CONVERTERS, cli
from ..config import SavedSettings
from ..errors import CLIError, ProdigyTeamsErrors
from ..messages import Messages
from ..prodigy_teams_broker_sdk.models import JobID, JobType
from ..prodigy_teams_pam_sdk import Client
from ..prodigy_teams_pam_sdk.models import (
    ActionCreating,
    ObjectValidation,
    RecipeDetail,
    RecipeListingLatest,
    RecipePlanCreating,
    TaskCreating,
)
from ..prodigy_teams_pam_sdk.recipe_utils import (
    Field,
    RecipeSchema,
    get_field_cli_args,
    get_field_optional,
    parse_plan,
)
from ..query import resolve_project_id
from ..ui import RecipeHelpFormatter, get_recipe_desc


def get_converter(arg_type: ty.Type) -> ty.Optional[ConverterType]:
    return CONVERTERS.get(arg_type, None)


def request_recipes(
    auth: CLIAuth, is_action: ty.Optional[bool] = None
) -> ty.Dict[str, RecipeDetail]:
    """Fetch all Recipes from Prodigy Teams
    auth (CLIAuth): CLI Auth object to handle auth to the Prodigy Teams API
    RETURNS (Tuple[Dict[str, RecipeDetail], Dict[str, RecipeDetail]]): Tuple of task_schemas, recipe_schemas
    """
    client = auth.client
    if client is None:
        return {}
    with msg.loading(Messages.T020):
        recipes = auth.retry(client.recipe.all_latest)(
            body=RecipeListingLatest(org_id=auth.org_id, broker_id=auth.broker_id)
        )
    schemas = {}
    for recipe in recipes.items:
        if is_action is None or recipe.is_action == is_action:
            schemas[recipe.name] = recipe
    return schemas


def create_from_recipe(
    recipe: RecipeDetail,
    args: ty.List[str],
    *,
    command: str,
    show_help: bool,
    exists_ok: bool = False,
) -> ty.Tuple[ty.UUID, RecipePlanCreating]:
    try:
        task_or_action_name, project_id, plan = _parse_plan(
            recipe,
            args,
            parser_prog=f"{cli.prog} {command} create {recipe.name.lower()}",
            show_help=show_help,
            get_project_id=_get_default_project_id,
        )
    except ShowHelp as e:
        print(e.help_text)
        sys.exit(1)
    auth = get_current_auth()
    object_validation = _get_object_validation(plan)
    if object_validation.errors:
        errors = ["\n".join(err) for err in object_validation.errors.values()]
        noun = "action" if recipe.is_action else "task"
        err = Messages.E044.format(noun=noun, name=task_or_action_name)
        raise CLIError(err, "\n".join(errors))
    _validate_plan(recipe, plan, object_validation)
    if recipe.is_action:
        job_id = _create_action(
            auth.client, task_or_action_name, project_id, plan, exists_ok=exists_ok
        )
    else:
        job_id = _create_task(
            auth.client, task_or_action_name, project_id, plan, exists_ok=exists_ok
        )
    return job_id.id, plan


def _parse_plan(
    recipe: RecipeDetail,
    args: ty.List[str],
    *,
    parser_prog: str,
    show_help: bool,
    get_project_id: ty.Callable[[], ty.Optional[ty.UUID]],
) -> ty.Tuple[str, ty.UUID, RecipePlanCreating]:
    # This function works hard to be pure and not rely on
    # external state. This way we'll be able to work with it in
    # the compatibility tests more easily.
    noun = "action" if recipe.is_action else "task"
    ap_args = _get_argparse_args(recipe)
    parser = _get_argparse_parser(parser_prog, recipe, ap_args)
    if not args or show_help:
        raise ShowHelp(parser.format_help())
    task_or_action_name, project_id, plan_args = _parse_cli_args(parser, args)
    missing = _check_missing(recipe, ap_args, plan_args)
    if missing:
        err = Messages.E001.format(noun=noun, name=task_or_action_name)
        raise CLIError(err, Messages.E043.format(args=", ".join(missing)))
    if project_id is None:
        project_id = get_project_id()
        if project_id is None:
            raise CLIError(Messages.E042.format(noun=noun, name=task_or_action_name))
    plan = RecipePlanCreating(
        recipe_id=recipe.id, project_id=project_id, args=plan_args
    )
    return task_or_action_name, project_id, plan


def _get_default_project_id() -> ty.Optional[ty.UUID]:
    project_id = SavedSettings.load().project
    if project_id is not None:
        project_id = resolve_project_id(project_id)
    return project_id


def _parse_cli_args(
    parser: ArgumentParser,
    args: ty.List[str],
) -> ty.Tuple[str, ty.Optional[ty.UUID], ty.Dict[str, Arg]]:
    parsed = vars(parser.parse_args(args))
    task_or_action_name = parsed.pop("name")
    assert isinstance(task_or_action_name, str)
    project_id = parsed.pop("project_id")
    if project_id is not None:
        project_id = ty.UUID(project_id)
    return (task_or_action_name, project_id, parsed)


def _check_missing(recipe: RecipeDetail, ap_args, parsed) -> ty.List[str]:
    optional = get_field_optional(recipe.form_schema)
    missing = []
    # We're iterating over the original args here because that gives us access
    # to the option names in the right CLI syntax
    for arg in ap_args:
        required = not optional.get(arg.id, True)
        if required and arg.id not in parsed:
            missing.append(arg.arg.option or arg.id)
    return missing


def _get_argparse_args(recipe: RecipeDetail) -> ty.List[ArgparseArg]:
    noun = "action" if recipe.is_action else "task"
    ap_args: ty.List[ArgparseArg] = []
    ap_args.append(get_arg("name", Arg(help=Messages.name.format(noun=noun)), str))
    for field in recipe.form_schema.fields:
        ap_args.extend(
            get_field_cli_args(
                ty.cast(Field, field), recipe.form_schema.cli_names or {}
            )
        )
    return ap_args


def _get_argparse_parser(
    prog: str, recipe: RecipeDetail, ap_args: ty.List[ArgparseArg]
) -> ArgumentParser:
    noun = "action" if recipe.is_action else "task"
    # To get argument parsing and consistent help docs out-of-the-box we create
    # a dummy parser with radicli's modified ArgumentParser (argparse subclass)
    p = ArgumentParser(
        prog=prog,
        description=get_recipe_desc(recipe),
        formatter_class=RecipeHelpFormatter,
    )
    for arg in ap_args:
        a_args, a_kwargs = arg.to_argparse()
        # We don't want defaults to creep in here, we want that to be
        # introduced at the last moment by the actual function.
        if "default" in a_kwargs:
            a_kwargs["default"] = DEFAULT_PLACEHOLDER
        p.add_argument(*a_args, **a_kwargs)
    # Add default arguments to all recipe CLIs
    pid_arg = Arg("--project-id", help=Messages.recipe_project_id.format(noun=noun))
    pid = get_arg("project_id", pid_arg, str, default=None)
    pid_args, pid_kwargs = pid.to_argparse()
    p.add_argument(*pid_args, **pid_kwargs)
    return p


def _get_object_validation(plan: RecipePlanCreating) -> ObjectValidation:
    auth = get_current_auth()
    object_validation = auth.client.recipeplan.validate_objects(plan)
    return object_validation


def _validate_plan(
    recipe: RecipeDetail,
    plan: RecipePlanCreating,
    object_validation: ObjectValidation,
) -> None:
    # Building a dummy objects map for parse_plan – the values don't matter,
    # since we're also only using a dummy fuction for create_custom_type
    objects_map = {"asset": {}, "dataset": {}}
    for field_type, objects in object_validation.existing.items():
        objects_map[field_type] = {arg: {} for arg in objects}
    for field_type, objects in object_validation.to_create.items():
        objects_map[field_type] = {arg: {} for arg in objects}
    parse_plan(
        ty.cast(RecipeSchema, recipe.form_schema),
        plan.args,
        objects_map,
        lambda x: lambda *a, **b: x,
    )


def _create_task(
    client: Client,
    name: str,
    project_id: ty.UUID,
    plan: RecipePlanCreating,
    exists_ok: bool = False,
) -> JobID:
    body = TaskCreating(name=name, project_id=project_id, plan=plan)
    try:
        task = client.task.create(body)
    except ProdigyTeamsErrors.ProjectNotFound:
        err = Messages.E013.format(name=project_id)
        raise CLIError(err)
    except ProdigyTeamsErrors.TaskExists:
        if exists_ok:
            msg.info(Messages.T001.format(noun="task", name=name))
            task = client.task.read(name=name, project_id=project_id)
            return JobID(id=task.id, job_type=JobType.task)
        err = Messages.E014.format(noun="task", name=name, project=project_id)
        raise CLIError(err)
    except ProdigyTeamsErrors.TaskInvalid:
        raise CLIError(Messages.E004.format(noun="task", name=name))
    return JobID(id=task.id, job_type=JobType.task)


def _create_action(
    client: Client,
    name: str,
    project_id: ty.UUID,
    plan: RecipePlanCreating,
    exists_ok: bool = False,
) -> JobID:
    body = ActionCreating(name=name, project_id=project_id, evaluation="", plan=plan)
    try:
        action = client.action.create(body)
    except ProdigyTeamsErrors.ProjectNotFound:
        err = Messages.E013.format(name=project_id)
        raise CLIError(err)
    except ProdigyTeamsErrors.ActionExists:
        if exists_ok:
            msg.info(Messages.T001.format(noun="action", name=name))
            action = client.action.read(name=name, project_id=project_id)
            return JobID(id=action.id, job_type=JobType.action)
        err = Messages.E014.format(noun="action", name=name, project=project_id)
        raise CLIError(err)
    except ProdigyTeamsErrors.ActionInvalid:
        raise CLIError(Messages.E004.format(noun="action", name=name))
    return JobID(id=action.id, job_type=JobType.action)


class ShowHelp(ValueError):
    def __init__(self, help_text: str):
        self.help_text = help_text
