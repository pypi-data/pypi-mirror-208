from radicli import Arg
from wasabi import msg

from .. import ty
from ..auth import get_current_auth
from ..cli import cli
from ..errors import BrokerError, CLIError
from ..messages import Messages
from ..prodigy_teams_broker_sdk.models import Secret, SecretResponse


@cli.subcommand(
    "consul",
    "create",
    key=Arg(help=Messages.path.format(noun="key")),
    value=Arg(help=Messages.value.format(noun="key")),
)
def create(key: str, value: str) -> None:
    """Create or update secret key and value"""
    auth = get_current_auth()
    try:
        auth.broker_client.consul.create(Secret(key=key, value=value))
    except BrokerError as e:
        raise CLIError(Messages.E001.format(noun="secret", name=key), e)
    msg.good(Messages.T002.format(noun="secret", name=key))


@cli.subcommand(
    "consul",
    "info",
    key=Arg(help=Messages.path.format(noun="key")),
)
def info(key: str) -> ty.Optional[ty.List[SecretResponse]]:
    """Get information related to secret key"""
    auth = get_current_auth()
    try:
        res = auth.broker_client.consul.read(key=key)
    except BrokerError as e:
        raise CLIError(Messages.E008.format(noun="secret", name=key), e)
    msg.table({o.Key: o.Value for o in res}, header=["key", "value"])
    return res


@cli.subcommand(
    "consul",
    "delete",
    key=Arg(help=Messages.path.format(noun="key")),
)
def delete(key: str) -> bool:
    """Delete a secret from a broker cluster"""
    auth = get_current_auth()
    try:
        res = auth.broker_client.consul.delete(key=key)
    except BrokerError as e:
        raise CLIError(Messages.E005.format(noun="secret", name=key), e)
    msg.good(Messages.T003.format(noun="secret", name=key))
    return res
