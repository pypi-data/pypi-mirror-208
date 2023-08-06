import os
import os.path
from itertools import chain
from pathlib import Path

from radicli import Arg

from ... import ty
from ...auth import get_current_auth
from ...cli import cli
from ...config import SavedSettings
from ...errors import BrokerError, CLIError
from ...messages import Messages
from ...prodigy_teams_broker_sdk import Client as BrokerClient
from ...prodigy_teams_broker_sdk import models as broker_models
from ...ui import Progress
from ...util import is_local, resolve_remote_path


class RsyncCallable(ty.Protocol):
    def __call__(
        self,
        *,
        src: str,
        dest: str,
        broker_client: BrokerClient,
    ) -> ty.Optional[str]:
        ...


@cli.subcommand(
    "files",
    "rsync",
    src=Arg(help=Messages.remote_local_path.format(noun="source")),
    dest=Arg(help=Messages.remote_local_path.format(noun="destination")),
    cluster_host=Arg("--cluster-host", help=Messages.cluster_host),
)
def rsync(src: str, dest: str, cluster_host: ty.Optional[str] = None) -> None:
    """Rsync files to and from the cluster"""
    broker_host = SavedSettings.get_and_save("broker_host", cluster_host)
    auth = get_current_auth()
    is_src_local = is_local(src)
    is_dest_local = is_local(dest)

    def _rsync(f: RsyncCallable, *, src, dest) -> ty.Optional[str]:
        return f(
            src=src,
            dest=dest,
            broker_client=auth.broker_client,
        )

    if is_src_local and is_dest_local:
        raise CLIError(Messages.E015.format(verb="rsync"), f"{src} -> {dest}")
    elif is_src_local and not is_dest_local:
        _rsync(
            _rsync_upload,
            src=src,
            dest=resolve_remote_path(auth.client, dest, broker_host),
        )
    elif not is_src_local and is_dest_local:
        _rsync(
            _rsync_download,
            src=resolve_remote_path(auth.client, src, broker_host),
            dest=dest,
        )
    else:
        _rsync(
            _rsync_on_remote,
            src=resolve_remote_path(auth.client, src, broker_host),
            dest=resolve_remote_path(auth.client, dest, broker_host),
        )


T1 = ty.TypeVar("T1")
T2 = ty.TypeVar("T2")
R = ty.TypeVar("R")


def diff(
    left: ty.List[T1],
    right: ty.List[T2],
    left_key: ty.Callable[[T1], R],
    right_key: ty.Callable[[T2], R],
) -> ty.Tuple[ty.List[T1], ty.List[T2]]:
    left_idx = {left_key(value): value for value in left}
    right_idx = {right_key(value): value for value in right}
    left_result = [left_idx[k] for k in left_idx.keys() - right_idx.keys()]
    right_result = [right_idx[k] for k in right_idx.keys() - left_idx.keys()]
    return left_result, right_result


def _rsync_upload(
    *,
    broker_client: BrokerClient,
    src: str,
    dest: str,
) -> None:
    src_path = Path(src).resolve().absolute()
    src = str(src_path)
    src_paths = sorted(
        [
            str(path.resolve().absolute())
            for path in chain((src_path,), src_path.glob("**/*"))
            if path.is_file()
        ],
        key=lambda path: path.removeprefix(src),
    )
    body = broker_models.Listing(path=dest, recurse=True, include_stats=False)
    try:
        files = broker_client.files.list_dir(body)
    except BrokerError as e:
        raise CLIError(Messages.E018, e)
    dest_paths = sorted(
        files.paths,
        key=lambda path: path.removeprefix(dest),
    )
    to_copy, to_delete = diff(
        src_paths,
        dest_paths,
        left_key=lambda path: path.removeprefix(src),
        right_key=lambda path: path.removeprefix(dest),
    )
    _rsync_upload_util(
        src_base=src,
        dest_base=dest,
        to_copy=to_copy,
        to_delete=to_delete,
        broker_client=broker_client,
    )


def _rsync_upload_util(
    *,
    src_base: str,
    dest_base: str,
    to_copy: ty.List[str],
    to_delete: ty.List[str],
    broker_client,
) -> None:
    def get_dest(path: str) -> str:
        return os.path.join(dest_base, path.removeprefix(src_base).removeprefix("/"))

    with Progress(to_copy) as paths:
        for path in paths:
            body = Path(path).open("rb").read()
            try:
                broker_client.files.upload(
                    body, dest=get_dest(path), overwrite=True, make_dirs=True
                )
            except BrokerError as e:
                raise CLIError(Messages.E017.format(verb="upload"), e)
    with Progress(to_delete) as paths:
        for path in paths:
            body = broker_models.Deleting(path=path, missing_ok=False)
            try:
                broker_client.files.delete(body)
            except BrokerError as e:
                raise CLIError(Messages.E017.format(verb="delete"), e)


def _rsync_download(
    *,
    broker_client: BrokerClient,
    src: str,
    dest: str,
) -> None:
    body = broker_models.Listing(path=src, recurse=True, include_stats=False)
    try:
        paths = broker_client.files.list_dir(body)
    except BrokerError as e:
        raise CLIError(Messages.E018, e)
    src_paths = sorted(paths.paths)
    if src_paths == src:
        raise CLIError(Messages.E024, src)
    dest_path = Path(dest).resolve().absolute()
    dest = str(dest_path)
    dest_paths = sorted(
        [
            str(path.resolve().absolute())
            for path in chain((dest_path,), dest_path.glob("**/*"))
            if path.is_file()
        ],
    )
    to_copy, to_delete = diff(
        src_paths,
        dest_paths,
        left_key=lambda path: path.removeprefix(src),
        right_key=lambda path: path.removeprefix(dest),
    )
    _rsync_download_util(
        src_base=src,
        dest_base=dest,
        to_copy=to_copy,
        to_delete=to_delete,
        broker_client=broker_client,
    )


def _rsync_download_util(
    *,
    src_base: str,
    dest_base: str,
    to_copy: ty.List[str],
    to_delete: ty.List[str],
    broker_client: BrokerClient,
) -> None:
    def get_dest(path: str) -> str:
        return os.path.join(dest_base, path.removeprefix(src_base).removeprefix("/"))

    with Progress(to_copy) as paths:
        for path in paths:
            body = broker_models.Downloading(target=path)
            try:
                content = broker_client.files.download(body)
            except BrokerError as e:
                raise CLIError(Messages.E017.format(verb="download"), e)
            dest = Path(get_dest(path))
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("wb") as file_:
                file_.write(content.read())
    with Progress(to_delete) as paths:
        for path in paths:
            path = Path(path)
            if path.exists():
                path.unlink()


def _rsync_on_remote(
    *,
    broker_client: BrokerClient,
    src: str,
    dest: str,
) -> None:
    body = broker_models.Copying(src=src, dest=dest, make_dirs=True, overwrite=True)
    try:
        plan = broker_client.files.plan_directory_rsync(body)
    except BrokerError as e:
        raise CLIError(Messages.E022, e)
    with Progress(plan.copy_) as copies:
        for file_copy_plan in copies:
            body = broker_models.Copying(
                src=file_copy_plan.src,
                dest=file_copy_plan.dest,
                make_dirs=True,
                overwrite=True,
            )
            try:
                broker_client.files.copy(body)
            except BrokerError as e:
                raise CLIError(Messages.E017.format(verb="copy"), e)
    with Progress(plan.delete) as paths:
        for path in paths:
            body = broker_models.Deleting(path=path, missing_ok=False)
            try:
                broker_client.files.delete(body)
            except BrokerError as e:
                raise CLIError(Messages.E017.format(verb="delete"), e)
