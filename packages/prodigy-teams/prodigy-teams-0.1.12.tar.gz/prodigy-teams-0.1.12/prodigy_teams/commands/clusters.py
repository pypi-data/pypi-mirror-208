import json
import time

import httpx
from radicli import Arg
from wasabi import msg

from .. import ty
from ..auth import get_current_auth
from ..cli import cli
from ..errors import (
    ConnectError,
    ConnectTimeout,
    HTTPStatusError,
    InvalidURL,
    RequestError,
)
from ..messages import Messages
from ..prodigy_teams_broker_sdk.models import CheckProgressRequest, CheckStartRequest
from ..prodigy_teams_pam_sdk import models as prodigy_teams_pam_sdk_models
from ..prodigy_teams_pam_sdk.models import BrokerUpdating
from ..query import resolve_broker, resolve_broker_id, resolve_package, resolve_recipe
from ..ui import print_info_table, print_table_with_select
from ..util import URL

# Broker has wrong name on infra
# TODO: Basic crud stuff here for clusters


def check_broker_status(
    broker: prodigy_teams_pam_sdk_models.BrokerReturning,
) -> ty.BrokerStatusCheck:
    url = URL.parse(broker.address) / "api/v1/status"
    # Before querying the broker, verify that it has finished registration
    # TODO: also track when it is killed in PAM
    if broker.state == "creating":
        return ty.BrokerStatusCheck.CREATING
    try:
        response = httpx.get(str(url))
        response.raise_for_status()
        payload = response.json()
        # Happy case: successfully connect to the broker and check "cluster" key
        if payload["cluster"] == "Ready":
            return ty.BrokerStatusCheck.RUNNING
        else:
            return ty.BrokerStatusCheck.ISSUES
    except InvalidURL:
        return ty.BrokerStatusCheck.INVALID_ADDRESS
    except (ConnectTimeout, ConnectError):
        # This could mean the broker is down, but could also mean we have no network access
        return ty.BrokerStatusCheck.NOT_FOUND
    except RequestError as e:
        msg.warn(Messages.E041.format(name=broker.name), str(e))
        return ty.BrokerStatusCheck.REQUEST_ERROR
    except HTTPStatusError as e:
        # We shouldn't really log here -- better to refactor this into the commands
        msg.warn(Messages.E041.format(name=broker.name), str(e.response.status_code))
        return ty.BrokerStatusCheck.RESPONSE_ERROR


class BrokerReturning(prodigy_teams_pam_sdk_models.BrokerReturning):
    """
    Extends the data returned by the API with computed properties.
    This is a workaround for the models being auto-generated.
    """

    @property
    def status(self) -> str:
        status = check_broker_status(self)
        return str(status)

    @classmethod
    def get_properties(cls) -> ty.List[str]:
        return [
            prop for prop in cls.__dict__ if isinstance(cls.__dict__[prop], property)
        ]

    def _iter(
        self,
        to_dict: bool = False,
        by_alias: bool = False,
        include=None,
        exclude=None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        exclude_properties: bool = False,
    ) -> ty.Iterator[ty.Tuple[str, ty.Any]]:
        yield from super()._iter(
            to_dict=to_dict,
            by_alias=by_alias,
            include=include,  # type: ignore
            exclude=exclude,  # type: ignore
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        if not exclude_properties:
            props = self.get_properties()
            if include:
                props = [prop for prop in props if prop in include]
            if exclude:
                props = [prop for prop in props if prop not in exclude]
            for key in props:
                yield key, getattr(self, key)


@cli.subcommand(
    "clusters",
    "list",
    # fmt: off
    select=Arg("--select", help=Messages.select.format(opts=list(BrokerReturning.__fields__))),
    # fmt: on
)
def list(
    select: ty.List[str] = ["id", "name", "status", "address"]
) -> ty.List[BrokerReturning]:
    """List resources on the cluster"""
    client = get_current_auth().client
    # TODO: this sequentially checks broker status which could be slow
    res = [
        BrokerReturning(**x.dict()) for x in client.broker.all(page=1, size=100).items
    ]
    print_table_with_select(res, select=select)
    return res


@cli.subcommand(
    "clusters",
    "info",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="cluster")),
    as_json=Arg("--json", help=Messages.as_json),
)
def info(name_or_id: ty.StrOrUUID, as_json: bool = False) -> BrokerReturning:
    """Get detailed info for a cluster"""
    cluster = BrokerReturning(**resolve_broker(name_or_id).dict())
    select = [*BrokerReturning.__fields__.keys(), *BrokerReturning.get_properties()]
    print_info_table(cluster, select=select, as_json=as_json)
    return cluster


@cli.subcommand(
    "clusters",
    "update",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="cluster")),
    name=Arg("--new-name", help=Messages.new_name.format(noun="cluster")),
    address=Arg("--address", help=Messages.new_address.format(noun="cluster")),
    as_json=Arg("--json", help=Messages.as_json),
)
def update(
    name_or_id: ty.StrOrUUID,
    name: ty.Optional[str] = None,
    address: ty.Optional[str] = None,
    as_json: bool = False,
) -> ty.UUID:
    """Update the cluster info"""
    cluster = resolve_broker(name_or_id)
    # TODO: The BrokerUpdating model is currently wrong on pam, making these
    # fields required. Change the query when this is fixed.
    body = BrokerUpdating(
        id=cluster.id, name=name or cluster.name, address=address or cluster.address
    )
    auth = get_current_auth()
    res = auth.client.broker.update(body)
    print_info_table(res, as_json=as_json)
    return cluster.id


@cli.subcommand(
    "clusters",
    "delete",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="cluster")),
)
def delete(name_or_id: ty.StrOrUUID) -> ty.UUID:
    """
    Delete a cluster from PAM. This only removes PAM's record
    of it. The cluster itself will continue to exist - you need
    to shut it down separately.
    """
    auth = get_current_auth()
    client = auth.client
    cluster_id = resolve_broker_id(name_or_id)
    client.broker.delete(id=cluster_id)
    msg.good(Messages.T003.format(noun="cluster", name=cluster_id))
    return cluster_id


@cli.subcommand(
    "clusters",
    "check",
    s3_bucket=Arg("--s3-bucket", help=Messages.check_s3_bucket),
    nfs_path=Arg("--nfs-path", help=Messages.check_nfs_path),
    recipe_name_or_id=Arg("--recipe", help=Messages.check_recipe),
    recipe_args=Arg("--recipe-args", help=Messages.check_recipe_args),
)
def check(
    s3_bucket: ty.Optional[str] = None,
    nfs_path: ty.Optional[str] = None,
    recipe_name_or_id: ty.Optional[ty.StrOrUUID] = None,
    recipe_args: ty.Optional[str] = None,
) -> None:
    """Check the cluster deployment went well"""
    auth = get_current_auth()
    if recipe_args:
        recipe_args_dict = json.loads(recipe_args)
        assert isinstance(recipe_args_dict, dict)
    else:
        recipe_args_dict = {}
    if recipe_name_or_id:
        recipe = resolve_recipe(recipe_name_or_id, broker_id=None)
        package = resolve_package(recipe.package_id, broker_id=None)
        recipe_name = recipe.name
        package_environment = package.environment
    else:
        recipe_name = None
        package_environment = None
    body = CheckStartRequest(
        s3_bucket=s3_bucket,
        nfs_path=nfs_path,
        package_environment=package_environment,
        recipe_name=recipe_name,
        recipe_args=recipe_args_dict,
    )
    start_response = auth.broker_client.check.start(body)
    while True:
        body = CheckProgressRequest(id=start_response.id)
        progress_response = auth.broker_client.check.progress(body)
        if progress_response.status == "done":
            assert progress_response.report
            msg.table(
                [x for x in progress_response.report.items()],  # type: ignore
                header=["Check Name", "Result"],
                divider=True,
            )
            break
        time.sleep(1)
