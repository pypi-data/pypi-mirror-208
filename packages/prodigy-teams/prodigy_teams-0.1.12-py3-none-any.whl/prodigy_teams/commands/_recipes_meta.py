"""Generate a wheel for a prodigy_teams_recipes package,
including updating its meta file and requirements files."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

import pkginfo

from .. import ty


def build_wheel(src: Path, wheelhouse: Path, use_active_venv: bool) -> Path:
    with _make_tempdir() as tmp:
        if use_active_venv:
            python = sys.executable
        else:
            venv_path = tmp / "venv"
            _subprocess_run(
                [sys.executable, "-m", "venv", str(venv_path.absolute())], tmp
            )
            python = (venv_path / "bin" / "python").absolute()
            _subprocess_run(
                [str(python), "-m", "pip", "install", "--upgrade", "pip", "wheel"],
                tmp,
            )
        ret = _subprocess_run(
            [
                str(python),
                "-m",
                "pip",
                "wheel",
                str(src.absolute()),
                "-f",
                str(wheelhouse.absolute()),
                "-w",
                str(wheelhouse.absolute()),
                "--no-deps",
                "--no-cache-dir",
            ],
            tmp,
        )
    filename = re.findall(r"(?<=filename=)\S+", ret.stdout)[-1]
    wheel = wheelhouse / filename
    assert wheel.exists()
    return wheel.absolute()


def compute_recipes_meta(
    wheel: Path, wheelhouse: Path, use_active_venv: bool
) -> ty.Dict[str, ty.Any]:
    pkg = pkginfo.Wheel(str(wheel.resolve()))
    assert pkg.name is not None
    assert pkg.version is not None
    name = pkg.name
    requirements = _resolve_requirements(
        f"{name}=={pkg.version}", wheel, wheelhouse, use_active_venv
    )
    recipes_meta = _get_recipes_meta(
        name.replace("-", "_"), wheel, wheelhouse, use_active_venv
    )
    meta = {
        "name": name,
        "version": pkg.version,
        "description": pkg.summary,
        "author": pkg.author,
        "email": pkg.author_email,
        "url": pkg.home_page,
        "license": pkg.license,
        "assets": {},
        "recipes": recipes_meta,
        "requirements": requirements,
    }
    # Check it's json serializable
    _ = json.dumps(meta, indent=2)
    return meta


def _resolve_requirements(
    package_version: str, wheel: Path, wheelhouse: Path, use_active_venv: bool
) -> ty.List[str]:
    with _make_tempdir() as tmp:
        text = _exec_compile_requirements(
            sys.executable, tmp, package_version, wheel, wheelhouse, use_active_venv
        )
    lines = [line.strip() for line in text.strip().split("\n")]
    return [
        r
        for r in lines
        if r and not r.startswith("#") and not r.startswith("--find-links")
    ]


def _get_recipes_meta(
    name: str, src: Path, wheelhouse: Path, use_active_venv: bool
) -> ty.Dict[str, ty.Any]:
    with _make_tempdir() as tmp:
        _exec_get_recipes_meta(
            sys.executable,
            tmp,
            src,
            wheelhouse,
            name,
            use_active_venv,
            tmp / "recipes.json",
        )
        # Read meta
        with (tmp / "recipes.json").open("r") as file_:
            recipes = json.loads(file_.read().strip())
    return recipes


def _exec_compile_requirements(
    python: str,
    tmp: Path,
    package_version: str,
    wheel: Path,
    wheelhouse: Path,
    use_active_venv: bool,
) -> str:
    """Compile a set of requirements inside a Python virtualenv using `pip-tools`."""
    if not use_active_venv:
        venv_path = tmp / "venv"
        _subprocess_run([python, "-m", "venv", str(venv_path.absolute())], tmp)
        python = str((venv_path / "bin" / "python").absolute())
        pip_compile = str((venv_path / "bin" / "pip-compile").absolute())
        # Install pip-tools
        _subprocess_run(
            [
                python,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip-tools",
            ],
            tmp,
        )
    else:
        pip_compile = "pip-compile"
    with (tmp / "reqs-in.txt").open("w") as file_:
        file_.write(package_version)
    # Run pip-compile
    _subprocess_run(
        [
            pip_compile,
            str((tmp / "reqs-in.txt").absolute()),
            "--output-file",
            str((tmp / "requirements.txt").absolute()),
            "-f",
            str(wheelhouse.absolute()),
            "--no-emit-find-links",
            # I was having weird problems if we don't rebuild, it seems
            # pip-tools will cache the result? That's not necessarily
            # what we want if you're developing and might not have changed
            # the version
            "--rebuild",
        ],
        tmp,
    )
    with (tmp / "requirements.txt").open(encoding="utf8") as file_:
        requirements = file_.read()
    return requirements


def _exec_get_recipes_meta(
    python: str,
    tmp: Path,
    src: Path,
    wheelhouse: Path,
    name: str,
    use_active_venv: bool,
    meta_path: Path,
) -> None:
    """Compile a set of requirements inside a Python virtualenv using `pip-tools`."""
    if not use_active_venv:
        venv_path = tmp / "venv"
        _subprocess_run([python, "-m", "venv", str(venv_path.absolute())], tmp)
        python = str((venv_path / "bin" / "python").absolute())
        # Install the package
        _subprocess_run(
            [
                python,
                "-m",
                "pip",
                "install",
                str(src.absolute()),
                "-f",
                str(wheelhouse.absolute()),
            ],
            tmp,
        )
    imports = f"{name}"
    _subprocess_run(
        [
            python,
            "-m",
            "prodigy_teams_recipes_sdk",
            "create-meta",
            imports,
            "--output",
            str(meta_path.absolute()),
        ],
        tmp,
    )


def _subprocess_run(args: ty.List[str], cwd: Path) -> subprocess.CompletedProcess:
    try:
        ret = subprocess.run(
            args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            text=True,
            encoding="utf8",
        )
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise
    return ret


@contextmanager
def _make_tempdir() -> ty.Generator[Path, None, None]:
    """Execute a block in a temporary directory and remove the directory and
    its contents at the end of the with block.

    YIELDS (Path): The path of the temp directory.
    """
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(str(d))
