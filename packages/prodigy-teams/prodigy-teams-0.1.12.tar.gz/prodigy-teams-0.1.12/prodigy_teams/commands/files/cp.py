import os
import os.path
from pathlib import Path

from radicli import Arg
from wasabi import msg

from ... import ty
from ...auth import get_current_auth
from ...cli import cli
from ...config import SavedSettings
from ...errors import BrokerError, CLIError
from ...messages import Messages
from ...prodigy_teams_broker_sdk import Client as BrokerClient
from ...prodigy_teams_broker_sdk import models as broker_models
from ...ui import Progress, is_silent
from ...util import is_local, resolve_remote_path


class CopyCallable(ty.Protocol):
    def __call__(
        self,
        *,
        src: str,
        dest: str,
        overwrite: bool,
        recurse: bool,
        make_dirs: bool,
        broker_client: BrokerClient,
    ) -> ty.Optional[str]:
        ...


@cli.subcommand(
    "files",
    "cp",
    src=Arg(help=Messages.remote_local_path.format(noun="source")),
    dest=Arg(help=Messages.remote_local_path.format(noun="destination")),
    recurse=Arg("--recurse", "-r", help=Messages.recurse_copy),
    make_dirs=Arg("--make-dirs", help=Messages.make_dirs),
    overwrite=Arg("--overwrite", help=Messages.overwrite),
    cluster_host=Arg("--cluster-host", help=Messages.cluster_host),
)
def cp(
    src: str,
    dest: str,
    recurse: bool = False,
    make_dirs: bool = False,
    overwrite: bool = False,
    cluster_host: ty.Optional[str] = None,
) -> None:
    """Copy files to and from the cluster"""
    broker_host = SavedSettings.get_and_save("broker_host", cluster_host)
    auth = get_current_auth()
    is_src_local = is_local(src)
    is_dest_local = is_local(dest)

    def _cp(f: CopyCallable, *, src: str, dest: str) -> ty.Optional[str]:
        return f(
            src=src,
            dest=dest,
            overwrite=overwrite,
            recurse=recurse,
            make_dirs=make_dirs,
            broker_client=auth.broker_client,
        )

    if is_src_local and is_dest_local:  # both local
        raise CLIError(Messages.E015.format(verb="copy"), f"{src}, {dest}")
    elif is_src_local and not is_dest_local:  # from local to remote
        err = _cp(
            _upload,
            src=src,
            dest=resolve_remote_path(auth.client, dest, broker_host),
        )
    elif not is_src_local and is_dest_local:
        # From remote to local
        err = _cp(
            _download,
            src=resolve_remote_path(auth.client, src, broker_host),
            dest=dest,
        )
    else:
        # Both remote
        err = _cp(
            _copy_on_remote,
            src=resolve_remote_path(auth.client, src, broker_host),
            dest=resolve_remote_path(auth.client, dest, broker_host),
        )
    if err is not None:
        raise CLIError(err)
    elif not is_silent():
        msg.good(Messages.T011, f"{src} -> {dest}")


def _upload(
    *,
    src: str,
    dest: str,
    make_dirs: bool,
    overwrite: bool,
    recurse: bool,
    broker_client: BrokerClient,
) -> ty.Optional[str]:
    src_path = Path(src)
    if src_path.is_dir() and not recurse:
        raise CLIError(Messages.E016, src_path)
    if src_path.is_dir():
        paths = [path for path in src_path.glob("**/*") if path.is_file()]
    else:
        paths = [src_path]
        src_path = src_path.parent

    def get_dest(path):
        return os.path.join(dest, str(path.relative_to(src_path)))

    with Progress(paths) as paths:
        for path in paths:
            body = path.open("rb")
            try:
                broker_client.files.upload(
                    body, dest=get_dest(path), overwrite=overwrite, make_dirs=make_dirs
                )
            except BrokerError as e:
                raise CLIError(Messages.E017.format(verb="upload"), e)


def _download(
    *,
    src: str,
    dest: str,
    make_dirs: bool,
    overwrite: bool,
    recurse: bool,
    broker_client: BrokerClient,
) -> ty.Optional[str]:
    body = broker_models.Listing(path=src, recurse=recurse, include_stats=False)
    try:
        files = broker_client.files.list_dir(body)
    except BrokerError as e:
        raise CLIError(Messages.E018, e)
    if not recurse:
        if len(files.paths) > 1:
            raise CLIError(Messages.E019, src)

    get_dest: ty.Callable[[str], Path] = (
        (lambda _: Path(dest))
        if not recurse
        # Important: we need to do str(Path()) here to ensure a trailing slash is
        # included. Otherwise, we end up with x / '/foo', which becomes '/foo'
        # and NOT x/foo, which would be expected!
        else lambda path: Path(dest) / (path.removeprefix(str(Path(src))))
    )
    with Progress(files.paths) as paths:
        for path in paths:
            dest_ = get_dest(path)
            if not overwrite and dest_.exists():
                raise CLIError(Messages.E020, dest_)
            if make_dirs:
                dest_.parent.mkdir(parents=True, exist_ok=True)
            elif not dest_.parent.exists():
                raise CLIError(Messages.E021, dest_)
            body = broker_models.Downloading(target=path)
            try:
                content = broker_client.files.download(body)
            except BrokerError as e:
                raise CLIError(Messages.E017.format(verb="download"), e)
            with dest_.open("wb") as file_:
                file_.write(content.read())


def _copy_on_remote(
    *,
    src: str,
    dest: str,
    make_dirs: bool,
    overwrite: bool,
    recurse: bool,
    broker_client: BrokerClient,
) -> ty.Optional[str]:
    if recurse:
        body = broker_models.Copying(
            src=src, dest=dest, make_dirs=make_dirs, overwrite=overwrite
        )
        try:
            plan = broker_client.files.plan_directory_copy(body)
        except BrokerError as e:
            raise CLIError(Messages.E022, e)
        copies = plan.copy_
    else:
        copies = [
            broker_models.Copying(
                src=src, dest=dest, make_dirs=make_dirs, overwrite=overwrite
            )
        ]
    with Progress(copies) as copies:
        for file_copy_plan in copies:
            body = broker_models.Copying(
                src=file_copy_plan.src,
                dest=file_copy_plan.dest,
                make_dirs=make_dirs,
                overwrite=overwrite,
            )
            try:
                broker_client.files.copy(body)
            except BrokerError as e:
                raise CLIError(Messages.E017.format(verb="copy"), e)
