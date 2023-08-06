import json
import os
import re
import shutil
import tarfile
import time
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

import packaging.tags
import packaging.utils
from radicli import Arg
from wasabi import msg

from .. import ty
from ..auth import get_current_auth
from ..cli import cli
from ..errors import BrokerError, CLIError
from ..messages import Messages
from ..prodigy_teams_broker_sdk import Client as BrokerClient
from ..prodigy_teams_broker_sdk import models as broker_models
from ..prodigy_teams_pam_sdk import Client
from ..prodigy_teams_pam_sdk.models import (
    PackageCreating,
    PackageReading,
    RecipeCreating,
    RecipeDetail,
    RecipeListingLatest,
    RecipeReturning,
)
from ..query import resolve_recipe
from ..ui import dicts_to_table, print_info_table, print_table_with_select
from ..util import resolve_remote_path
from ._recipes_meta import build_wheel, compute_recipes_meta

COOKIECUTTER_PATH = Path(__file__).parent.parent / "recipes_cookiecutter"


@cli.subcommand("recipes", "list")
def list() -> ty.Sequence[RecipeReturning]:
    """List all recipes"""
    auth = get_current_auth()
    # When there are multiple versions of a package publishing some recipe, only
    # list the latest version.
    res = auth.client.recipe.all_latest(
        body=RecipeListingLatest(broker_id=auth.broker_id, org_id=auth.org_id)
    )
    print_table_with_select(res.items, ["id", "name"])
    return res.items


@cli.subcommand(
    "recipes",
    "info",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="recipe")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="recipe")),
    as_json=Arg("--json", help=Messages.as_json),
)
def info(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    as_json: bool = False,
) -> RecipeDetail:
    """Show info about a recipe"""
    auth = get_current_auth()
    if cluster_id is None:
        cluster_id = auth.broker_id
    res = resolve_recipe(name_or_id, broker_id=cluster_id)
    print_info_table(res, as_json=as_json)
    return res


@cli.subcommand(
    "recipes",
    "init",
    # fmt: off
    output_dir=Arg(help=Messages.output_dir.format(noun="recipe package")),
    name=Arg("--name", help=Messages.name.format(noun="package (e.g. custom_recipes)")),
    version=Arg("--version", help=Messages.version.format(noun="package")),
    description=Arg("--description", help=Messages.description.format(noun="package")),
    author=Arg("--author", help=Messages.name.format(noun="package author")),
    email=Arg("--email", help=Messages.email.format(noun="package author")),
    url=Arg("--url", help=Messages.url.format(noun="package")),
    license=Arg("--license", help=Messages.license.format(noun="package")),
    # fmt: on
)
def init(
    output_dir: Path,
    name: ty.Optional[str] = None,
    version: str = "0.1.0",
    description: str = "",
    author: str = "",
    email: str = "",
    url: str = "",
    license: str = "",
) -> None:
    """Generate a new recipes Python package"""
    # output_dir is passed as the path to the package itself, but our template
    # structure includes the package directory under the `package_dir` key.
    package_dir = output_dir.resolve()
    parent_dir = package_dir.parent.resolve()
    package_dir = package_dir.name
    # Infer a default package name from the directory path
    name = name or package_dir
    # Create a wheel-friendly package name slug
    package_name = re.sub(r"[^\w\d.]+", "_", name.lower(), re.UNICODE)
    template_dir = COOKIECUTTER_PATH
    variables = {
        "name": name,  # human friendly recipe package name
        "version": version,
        "short_description": description,
        "author": author,
        "email": email,
        "url": url,
        "license": license,
        "parent_dir": str(parent_dir),  # the directory path containing the package
        "package_dir": package_dir,  # top-level package directory within `parent_dir`
        "package_name": package_name,  # the normalized name of the package
    }
    if not _ensure_preconditions(template_dir, variables):
        msg.info(Messages.E154.format(name=name))
        return None
    _fill_template(template_dir, variables)
    msg.good(Messages.T002.format(noun="package", name=name), str(output_dir))


@cli.subcommand(
    "recipes",
    "verify",
    package=Arg(help=Messages.path.format(noun="package")),
)
def verify(package: ty.ExistingFilePath) -> None:
    """Verify a built recipe package before upload"""
    if not (package.name.endswith("tar.gz") or package.name.endswith(".whl")):
        raise CLIError(Messages.E144, package.name)
    file_name = ""
    meta_json = None
    valid_meta = False
    if package.name.endswith(".whl"):
        with ZipFile(package) as zip_file:
            for file_name in zip_file.namelist():
                if file_name.endswith("/meta.json"):
                    meta_bytes = zip_file.read(file_name)
                    meta_json = json.loads(meta_bytes.decode("utf-8"))
                    if not isinstance(meta_json, dict):
                        continue
                    if "prodigy_teams" in meta_json:
                        valid_meta = True
                        break
    elif package.name.endswith(".tar.gz"):
        with tarfile.open(package) as tar:
            for file_name in tar.getnames():
                if file_name.endswith("/meta.json"):
                    io_bytes = tar.extractfile(file_name)
                    assert io_bytes
                    meta_json = json.load(io_bytes)
                    if not isinstance(meta_json, dict):
                        continue
                    if "prodigy_teams" in meta_json:
                        valid_meta = True
                        break
    if not (valid_meta and meta_json):
        raise CLIError(Messages.E145)
    msg.good(Messages.T022, file_name)
    recipes_data = meta_json.get("prodigy_teams", {}).get("recipes")
    if not isinstance(recipes_data, dict):
        raise CLIError(Messages.E146, recipes_data)
    if not recipes_data:
        raise CLIError(Messages.E147, Messages.E148)
    recipes_info = []
    invalid_recipes = []
    for key, data in recipes_data.items():
        entry_point = data.get("entry_point")
        recipe_args = data.get("args")
        data = {
            "name": key,
            "entry_point": entry_point,
            "contains args": bool(recipe_args),
        }
        recipes_info.append(data)
        if not entry_point or not recipe_args:
            invalid_recipes.append(key)
    headers, rows = dicts_to_table(recipes_info)
    msg.good(Messages.T023)
    msg.table(rows, header=headers, divider=True, max_col=3000)
    if invalid_recipes:
        raise CLIError(Messages.E149, ", ".join(invalid_recipes))
    msg.good(Messages.T024)


@cli.subcommand(
    "recipes",
    "publish",
    # fmt: off
    src=Arg(help=Messages.local_path.format(noun="package")),
    wheelhouse=Arg(help=Messages.wheelhouse),
    cluster_wheels_path=Arg("--cluster-wheels-path", help=Messages.path.format(noun="cluster wheels")),  # TODO
    cluster_envs_path=Arg("--cluster-envs-path", help=Messages.path.format(noun="cluster envs")),  # TODO
    use_active_venv=Arg("--use-active-venv", help=Messages.use_active_venv),
    exists_ok=Arg("--exists-ok", help=Messages.exists_ok)
    # fmt: on
)
def publish(
    src: ty.ExistingDirPath,
    wheelhouse: Path,
    cluster_wheels_path: str = "{wheels}",
    cluster_envs_path: str = "{envs}",
    use_active_venv: bool = False,
    exists_ok: bool = False,
) -> ty.Optional[ty.UUID]:
    """
    Build, upload and advertise a recipes package from the local filesystem. The
    recipes package and any required dependencies are uploaded to the cluster,
    and then advertised to the PAM service.
    """
    auth = get_current_auth()
    if auth.broker_host is None:
        raise CLIError(Messages.E035)
    if auth.broker_id is None:
        raise CLIError(Messages.E036)
    # Before starting to build the wheel, do some work that could error. Building
    # the wheel and getting the metadata is slow, so we want to avoid it if possible.
    cluster_wheels_path = resolve_remote_path(
        auth.client, cluster_wheels_path, auth.broker_host
    )
    cluster_envs_path = resolve_remote_path(
        auth.client, cluster_envs_path, auth.broker_host
    )
    # Sync wheels to broker. We first calculate what files the broker needs to
    # fulfill the specified requirements.
    body = broker_models.Listing(
        path=cluster_wheels_path, recurse=True, include_stats=True
    )
    try:
        cluster_res = auth.broker_client.files.list_dir(body)
    except BrokerError as e:
        raise CLIError(Messages.E152, e)
    else:
        assert cluster_res.stats is not None
        cluster_wheels = {}
        for path, stats in zip(cluster_res.paths, cluster_res.stats):
            cluster_wheels[Path(path).name] = stats.size
    if src.is_dir():
        msg.info(Messages.T025.format(src=src))
        wheel = build_wheel(src, wheelhouse, use_active_venv)
    else:
        wheel = wheelhouse / src.name
        if src != wheel:
            shutil.copyfile(src, wheel)
    package_exists = _check_for_package(auth.client, auth.broker_id, wheel)
    if package_exists:
        if exists_ok:
            msg.info(Messages.T026.format(name=wheel.name))
            return None
        raise CLIError(Messages.E153.format(name=wheel.name))
    # Builds the package
    msg.info(Messages.T027.format(name=wheel.name))
    meta = compute_recipes_meta(wheel, wheelhouse, use_active_venv)
    msg.good(Messages.T028)
    msg.info(Messages.T029)
    to_upload = _plan_wheel_upload(
        wheel=wheel,
        requirements=meta["requirements"],
        wheelhouse=wheelhouse,
        cluster_wheels=cluster_wheels,
    )
    msg.info(Messages.T030.format(count=len(to_upload)))
    # Upload the wheels
    _upload_wheels(auth.broker_client, to_upload, cluster_wheels_path)
    msg.good(Messages.T028)
    # Create the environment. First we try non-blocking, but if that fails, we
    # try again with blocking to (hopefully!) surface the error.
    msg.info(Messages.T031)
    maybe_env_path = _create_environment(
        auth.broker_client,
        meta["requirements"],
        wheels_path=cluster_wheels_path,
        envs_path=cluster_envs_path,
        blocking=False,
    )
    if maybe_env_path is None:
        env_path = _create_environment(
            auth.broker_client,
            meta["requirements"],
            wheels_path=cluster_wheels_path,
            envs_path=cluster_envs_path,
            blocking=True,
        )
        assert env_path is not None
    else:
        env_path = maybe_env_path
    msg.good(Messages.T028)
    msg.info(Messages.T032)
    package_id = _publish_package_to_pam(
        auth.client,
        auth.broker_id,
        name=meta["name"],
        filename=wheel.name,
        version=meta["version"],
        meta=meta,
        environment=env_path,
    )
    msg.good(Messages.T028)
    return package_id


def _check_for_package(client: Client, broker_id: ty.UUID, wheel_path) -> bool:
    packages = client.package.all(
        PackageReading(
            broker_id=broker_id,
            filename=wheel_path.name,
            name=None,
            version=None,
            id=None,
            org_id=None,
        )
    )
    return bool(packages.items)


def _plan_wheel_upload(
    *,
    wheel: Path,
    requirements: ty.Set[str],
    wheelhouse: Path,
    cluster_wheels: ty.Dict[str, int],
) -> ty.List[Path]:
    needed = [wheel]
    for path in wheelhouse.iterdir():
        if path.name[0] == "." or path.suffix != ".whl":
            continue
        if (
            path.name in cluster_wheels
            and cluster_wheels[path.name] == path.stat().st_size
        ):
            continue
        if path.name == wheel.name:
            continue
        wheel_info = _WheelInfo.from_filename(path.name)
        if f"{wheel_info.name}=={wheel_info.version}" not in requirements:
            continue
        # TODO compatibility check
        # TODO check whether on public pypi?
        needed.append(path.absolute())
    return needed


def _upload_wheels(client: BrokerClient, srcs: ty.List[Path], dest: str) -> None:
    for src in srcs:
        with src.open("rb") as file_:
            client.files.upload(
                file_,
                dest=os.path.join(dest, src.name),
                make_dirs=True,
                overwrite=True,
            )
            msg.good(Messages.T033.format(src=src.name))


def _create_environment(
    client: BrokerClient,
    requirements: ty.List[str],
    wheels_path: str,
    envs_path: str,
    blocking: bool,
) -> ty.Optional[str]:
    body = broker_models.EnvCreating(
        requirements=requirements,
        wheels_path=wheels_path,
        envs_path=envs_path,
        blocking=blocking,
    )
    env = client.envs2.create(body)
    if blocking:
        # It's supposed to only return when the environment is ready if we told it to block
        assert env.ready
    else:
        for _ in range(50):
            if env.ready:
                return env.path
            else:
                time.sleep(10)
                env = client.envs2.await_env(broker_models.EnvAwaiting(path=env.path))
        return None


def _publish_package_to_pam(
    client: Client,
    broker_id: ty.UUID,
    *,
    name: str,
    filename: str,
    version: str,
    environment: str,
    meta: ty.Dict[str, ty.Any],
) -> ty.UUID:
    package = client.package.create(
        PackageCreating(
            name=name,
            filename=filename,
            version=version,
            broker_id=broker_id,
            environment=environment,
            meta=meta,
        )
    )
    msg.good(
        Messages.T002.format(noun="package", name=f"{package.name} ({package.id})")
    )
    for recipe_data in meta["recipes"]:
        # The recipe create-meta command is supposed to output
        # entries that match the RecipeCreating body, except
        # for missing a package_id
        body = RecipeCreating(**recipe_data, package_id=package.id)
        r = client.recipe.create(body)
        recipe_type = "action" if body.is_action is True else "task"
        msg.good(Messages.T002.format(noun=f"{recipe_type} recipe", name=r.name))
    return package.id


def _ensure_preconditions(template_dir: Path, variables: ty.Dict[str, ty.Any]) -> bool:
    output_dir = Path(variables["parent_dir"])
    if output_dir.exists() and output_dir.is_file():
        msg.fail(Messages.E002.format(noun="directory", name=str(output_dir)))
        return False
    conflicts = _find_overwrite_conflicts(template_dir, variables)
    if conflicts:
        for conflict_file in conflicts:
            msg.fail(Messages.E002.format(noun="file", name=str(conflict_file)))
        return False
    return True


def _find_overwrite_conflicts(
    template_dir: Path, variables: ty.Dict[str, ty.Any]
) -> ty.List[ty.Union[Path, "TemplateItem"]]:
    output_dir = Path(variables["parent_dir"])
    conflicts = []
    if output_dir.exists() and output_dir.is_dir():
        for tmpl in _walk_template(template_dir):
            out_file = tmpl.output_path(variables)
            if out_file.exists():
                conflicts.append(out_file)
    elif output_dir.exists() and output_dir.is_file():
        conflicts.append(output_dir)
    return conflicts


@dataclass
class TemplateItem:
    template_dir: Path
    template_path: Path

    def output_path(self, variables: ty.Dict[str, ty.Any]) -> Path:
        return Path(variables["parent_dir"]) / _replace_path_vars(
            self.template_path.relative_to(self.template_dir), variables
        )

    def expand(self, variables: ty.Dict[str, ty.Any]) -> str:
        with self.template_path.open("r", encoding="utf8") as file_:
            return _replace_content_vars(file_.read(), variables)


def _fill_template(template_dir: Path, variables: ty.Dict[str, ty.Any]) -> None:
    # TODO: check cookiecutter.json for defaults?
    for tmpl in _walk_template(template_dir):
        contents = tmpl.expand(variables)
        output_path = tmpl.output_path(variables)
        if output_path.name.endswith(".tmpl"):
            # We allow files to be named *.thing.tmpl to denote that it's a template
            # of a .thing file, but not currently a valid .thing file. We still might
            # replace variables in files named other things, if the variable substitution
            # doesn't change the syntactic validity of the file. So if we have a .tmpl
            # suffix, we just strip that.
            output_path = output_path.parent / output_path.name[: -len(".tmpl")]
        output_path.parent.mkdir(exist_ok=True, parents=True)
        with output_path.open("w", encoding="utf8") as file_:
            file_.write(contents)


def _replace_content_vars(
    contents: str,
    variables: ty.Dict[str, ty.Any],
    *,
    var_prefix="{{cookiecutter.",
    var_suffix="}}",
) -> str:
    for key, value in variables.items():
        key = f"{var_prefix}{key}{var_suffix}"
        contents = contents.replace(key, value)
    return contents


def _replace_path_vars(
    path: Path,
    variables: ty.Dict[str, ty.Any],
    *,
    var_prefix="{{cookiecutter.",
    var_suffix="}}",
) -> Path:
    """Given a path that might have variables, fill in the variables
    from a given dict.
    """
    parts = []
    for part in path.parts:
        if part.startswith(var_prefix) and part.endswith(var_suffix):
            variable = part[len(var_prefix) : -len(var_suffix)]
            part = variables[variable]
        parts.append(part)
    if not parts:
        return path
    else:
        return Path(parts[0]).joinpath(*parts[1:])


def _walk_template(template_dir: Path) -> ty.Iterable[TemplateItem]:
    def _walk(path: Path) -> ty.Iterable[Path]:
        for p in Path(path).iterdir():
            if p.is_dir():
                yield from _walk(p)
                continue
            if p.name == "cookiecutter.json":
                continue
            yield p

    for p in _walk(template_dir):
        yield TemplateItem(template_dir, p)


@dataclass
class _WheelInfo:
    filename: str
    name: str
    version: str
    build: ty.Optional[ty.Tuple[int, str]]
    tags: ty.Set[packaging.tags.Tag]

    @classmethod
    def from_filename(cls, filename: str) -> "_WheelInfo":
        name, version, build, tags = packaging.utils.parse_wheel_filename(filename)
        return cls(
            filename=filename,
            name=str(name),
            version=str(version),
            build=build if build else None,
            tags=set(tags),
        )
