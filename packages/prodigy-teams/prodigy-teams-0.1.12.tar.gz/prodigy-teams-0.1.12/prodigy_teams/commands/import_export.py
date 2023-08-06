import json
import os
import shlex
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from radicli import Arg
from wasabi import msg

from .. import ty
from ..cli import cli
from ..messages import Messages
from ..prodigy_teams_pam_sdk import models


class ProjectData(models.ProjectReturning):
    tasks: ty.Sequence[ty.List[str]] = tuple()
    actions: ty.Sequence[ty.List[str]] = tuple()
    # Setting some defaults for creation
    created: ty.datetime = datetime.now()
    updated: ty.datetime = datetime.now()
    id: ty.UUID = uuid.uuid4()
    org_id: ty.UUID = uuid.uuid4()


class AssetData(models.AssetReturning):
    dest: str  # destination for upload
    # Setting some defaults for creation
    created: ty.datetime = datetime.now()
    updated: ty.datetime = datetime.now()
    id: ty.UUID = uuid.uuid4()
    broker_id: ty.UUID = uuid.uuid4()
    num_used_by: int = 0


class DatasetData(models.DatasetReturning):
    # Setting some defaults for creation
    created: ty.datetime = datetime.now()
    updated: ty.datetime = datetime.now()
    id: ty.UUID = uuid.uuid4()
    broker_id: ty.UUID = uuid.uuid4()
    num_used_by: int = 0


class PathData(models.BrokerPathReturning):
    # Setting some defaults for creation
    created: ty.datetime = datetime.now()
    updated: ty.datetime = datetime.now()
    id: ty.UUID = uuid.uuid4()
    broker_id: ty.UUID = uuid.uuid4()


class RecipeData(ty.BaseModel):
    path: Path
    wheels_path: Path
    use_active_venv: bool
    cluster_envs_path: str
    cluster_wheels_path: str


class Data(ty.BaseModel):
    timestamp: ty.datetime = datetime.now()
    project: ty.Dict[str, ProjectData]
    asset: ty.Dict[str, AssetData]
    dataset: ty.Dict[str, DatasetData]
    path: ty.Dict[str, PathData]


@cli.command(
    "export",
    output=Arg(help=Messages.export_output),
    assets_dir=Arg(help=Messages.assets_dir),
    include=Arg("--include", help=Messages.include),
)
def export_data(
    # fmt: off
    output: ty.Path,
    assets_dir: ty.Optional[ty.Path] = None,
    include: ty.List[ty.Literal["tasks", "actions", "assets", "datasets", "paths"]] = ["tasks", "actions", "assets", "datasets", "paths"],
    # fmt: on
) -> None:
    """
    Save the state of the current app JSON file. If an assets directory is
    provided, assets will be downloaded and referenced in the JSON accordingly.
    """
    os.environ["PRODIGY_TEAMS_CLI_SILENT"] = "true"

    from prodigy_teams import commands as ptc
    from prodigy_teams.util import is_local

    result = Data(timestamp=datetime.now(), project={}, asset={}, dataset={}, path={})
    projects = ptc.projects.list()
    assets = ptc.assets.list()
    datasets = ptc.datasets.list()
    tasks = ptc.tasks.list()
    actions = ptc.actions.list()
    paths = ptc.paths.list()
    if "paths" in include:
        for path in paths:
            result.path[path.name] = PathData(**path.dict())
    tasks_by_project = defaultdict(list)
    actions_by_project = defaultdict(list)
    if "tasks" in include:
        for task in tasks:
            tasks_by_project[task.project_id].append(task)
    if "actions" in include:
        for action in actions:
            actions_by_project[action.project_id].append(action)
    for project in projects:
        info = ptc.projects.info(project.id)
        project_tasks = tasks_by_project.get(project.id, [])
        project_actions = actions_by_project.get(project.id, [])
        result.project[info.name] = ProjectData(
            **info.dict(),
            tasks=[_get_cmd(t.cli_command) for t in project_tasks],
            actions=[_get_cmd(a.cli_command) for a in project_actions],
        )
    if "assets" in include:
        assets_map = {}
        if assets_dir is not None and assets:
            assets_dir.mkdir(exist_ok=True, parents=True)
            msg.info(Messages.T035.format(count=len(assets)))
            for asset in assets:
                src = str(asset.path)
                if is_local(src):  # TODO: not sure what to do here
                    continue
                dest = str(assets_dir / src.rsplit("//", 1)[-1])
                ptc.files.cp(src, dest, recurse=True, make_dirs=True, overwrite=True)
                assets_map[asset.id] = str(dest)
            msg.good(Messages.T036)
        elif assets:
            msg.warn(Messages.T037)
        for asset in assets:
            asset.path = assets_map.get(asset.id, asset.path)
            result.asset[asset.name] = AssetData(**asset.dict(), dest=asset.path)
    if "datasets" in include:
        for dataset in datasets:
            result.dataset[dataset.name] = DatasetData(**dataset.dict())
    info_msg = Messages.T038.format(
        n_projects=len(result.project),
        n_tasks=sum(len(t) for t in tasks_by_project.values()),
        n_actions=sum(len(a) for a in actions_by_project.values()),
        n_assets=len(result.asset),
        n_datasets=len(result.dataset),
        n_paths=len(result.path),
    )
    msg.info(info_msg)
    with output.open("w", encoding="utf8") as f:
        f.write(result.json(indent=2))
    msg.good(Messages.T039, str(output))


@cli.command(
    "import",
    data=Arg(help=Messages.import_data),
    strict=Arg("--strict", "-S", help=Messages.import_strict),
)
def import_data(data: ty.Union[ty.Path, Data], strict: bool = False) -> None:
    """
    Populate Prodigy Teams with data for projects, tasks, actions, assets and paths.
    """
    _import_data(data, strict=strict)


def _import_data(
    data: ty.Union[ty.Path, Data],
    recipes: ty.List[RecipeData] = [],
    strict: bool = False,
) -> None:
    print(recipes)
    os.environ["PRODIGY_TEAMS_CLI_SILENT"] = "true"
    from prodigy_teams import commands as ptc

    if isinstance(data, ty.Path):
        with Path(data).open("r", encoding="utf8") as f:
            file_data = json.loads(f.read())
            assert isinstance(file_data, dict)
            data = Data(**file_data)

    if data.project:
        msg.divider(Messages.T040)
        for project in data.project.values():
            ptc.projects.create(project.name, project.description, exists_ok=not strict)
    if data.path:
        msg.divider(Messages.T041)
        for path in data.path.values():
            ptc.paths.create(path.name, path.path, exists_ok=not strict)
    # TODO: this is currently not exposed via the ptc CLI
    if recipes:
        msg.divider(Messages.T045)
        for recipe in recipes:
            ptc.recipes.publish(
                recipe.path,  # type: ignore
                recipe.wheels_path,
                exists_ok=not strict,
                use_active_venv=recipe.use_active_venv,
                cluster_envs_path=recipe.cluster_envs_path,
                cluster_wheels_path=recipe.cluster_wheels_path,
            )
    if data.asset:
        msg.divider(Messages.T042)
        for asset in data.asset.values():
            ptc.files.cp(
                asset.path,
                asset.dest,
                recurse=True,
                make_dirs=True,
                overwrite=not strict,
            )
        msg.divider(Messages.T043)
        for asset in data.asset.values():
            ptc.assets.create(
                asset.kind,
                asset.name,
                asset.dest,
                meta=json.dumps(asset.meta),
                exists_ok=not strict,
            )
    if data.project:
        msg.divider(Messages.T044)
        for project in data.project.values():
            if project.tasks or project.actions:
                ptc.config.project(project.name)
                for task in project.tasks:
                    ptc.tasks.create(_extra=task, exists_ok=not strict, no_start=True)
                for action in project.actions:
                    ptc.actions.create(
                        _extra=action, exists_ok=not strict, no_start=True
                    )


def _get_cmd(command: str) -> ty.List[str]:
    return shlex.split(command)[3:-2]
