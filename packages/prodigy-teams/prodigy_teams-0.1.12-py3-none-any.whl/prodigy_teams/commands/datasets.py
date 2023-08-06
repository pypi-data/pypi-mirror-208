from pathlib import Path

import srsly
from radicli import Arg
from wasabi import msg

from .. import ty
from ..auth import get_current_auth
from ..cli import cli
from ..errors import CLIError, ProdigyTeamsErrors
from ..messages import Messages
from ..prodigy_teams_pam_sdk.models import DatasetDetail, DatasetReturning
from ..query import collect_from_pages, resolve_dataset, resolve_dataset_id
from ..ui import PageProgress, print_info_table, print_table_with_select


@cli.subcommand(
    "datasets",
    "list",
    # fmt: off
    select=Arg("--select", help=Messages.select.format(opts=list(DatasetReturning.__fields__))),
    # fmt: on
)
def list(
    select: ty.List[str] = ["id", "name", "kind"]
) -> ty.Sequence[DatasetReturning]:
    """List all Datasets"""
    client = get_current_auth().client
    res = client.dataset.all()
    print_table_with_select(res.items, select=select)
    return res.items


@cli.subcommand(
    "datasets",
    "info",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="dataset")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="dataset")),
    as_json=Arg("--json", help=Messages.as_json),
)
def info(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    as_json: bool = False,
) -> DatasetReturning:
    """Get detailed info for a Dataset"""
    res = resolve_dataset(name_or_id, broker_id=cluster_id)
    print_info_table(res, as_json=as_json)
    return res


@cli.subcommand(
    "datasets",
    "create",
    name=Arg(help=Messages.name.format(noun="dataset")),
    kind=Arg("--kind", help=Messages.kind.format(noun="dataset")),
    exists_ok=Arg("--exists-ok", help=Messages.exists_ok),
)
def create(
    name: str, kind: str, exists_ok: bool = False
) -> ty.Union[DatasetReturning, DatasetDetail, None]:
    """Create a new dataset"""
    auth = get_current_auth()
    client = auth.client
    broker_id = auth.broker_id
    try:
        res = client.dataset.create(name=name, kind=kind, broker_id=broker_id)
    except ProdigyTeamsErrors.DatasetExists:
        if exists_ok:
            msg.info(Messages.T001.format(noun="dataset", name=name))
            return None
        raise CLIError(Messages.E002.format(noun="dataset", name=name))
    except ProdigyTeamsErrors.DatasetInvalid:
        raise CLIError(Messages.E004.format(noun="dataset", name=name))
    except ProdigyTeamsErrors.DatasetForbiddenCreate:
        raise CLIError(Messages.E003.format(noun="dataset", name=name))
    msg.divider("Dataset")
    msg.table(res.dict())
    return res


@cli.subcommand(
    "datasets",
    "delete",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="dataset")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="dataset")),
)
def delete(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
) -> ty.UUID:
    """Delete a dataset"""
    dataset_id = resolve_dataset_id(name_or_id, broker_id=cluster_id)
    auth = get_current_auth()
    try:
        auth.client.dataset.delete(id=dataset_id)
    except (
        ProdigyTeamsErrors.ProjectForbiddenDelete,
        ProdigyTeamsErrors.ProjectNotFound,
    ):
        raise CLIError(Messages.E006.format(noun="dataset", name=name_or_id))
    else:
        msg.good(Messages.T003.format(noun="dataset", name=name_or_id))
    return dataset_id


@cli.subcommand(
    "datasets",
    "export",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="dataset")),
    output_file=Arg("--output", "-o", help=Messages.export_output),
)
def export(
    name_or_id: ty.StrOrUUID,
    output_file: ty.Union[str, Path] = "-",
) -> None:
    """Export all the examples from a dataset and save it in the designated file as
    JSONL (newline-delimited JSON).
    """
    auth = get_current_auth()
    cluster_id = auth.broker_id

    dataset = resolve_dataset(name_or_id, broker_id=cluster_id)

    def get_examples_page(page: int):
        return auth.broker_client.datasets.read_examples(
            dataset.name,
            page=page,
        )

    with PageProgress(collect_from_pages(get_examples_page)) as pages:
        srsly.write_jsonl(
            output_file,
            (example.content for page in pages for example in page.items),
            append_new_line=False,
        )
