import logging
import os
import time
from pathlib import Path

import httpx
import pydantic
from pydantic import BaseModel

from . import ty
from .config import SavedSettings, config_dir
from .errors import (
    CLIError,
    HTTPError,
    ProdigyTeamsError,
    ProdigyTeamsIDTokenError,
    ProdigyTeamsParseSecretsError,
)
from .messages import Messages
from .prodigy_teams_broker_sdk import (
    AccessTokenCredential as BrokerAccessTokenCredential,
)
from .prodigy_teams_broker_sdk import Client as BrokerClient
from .prodigy_teams_pam_sdk import AccessTokenCredential, Client
from .prodigy_teams_pam_sdk.models import BrokerReading
from .ui import print_login_info
from .util import URL

logger = logging.getLogger(__name__)


AUTH0_SCOPE = "openid profile email"
AUTH0_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"
AUTH_WAIT_TIME_SECONDS = 60 * 5


class Secrets(ty.Protocol):
    """
    Defines the interface for secrets storage. During normal operation,
    the secrets are stored in a file on disk. During testing, a mock
    implementation can be used to prevent breaking configuration.
    """

    id_token: ty.Optional[str]
    api_token: ty.Optional[AccessTokenCredential]
    broker_tokens: ty.Dict[str, BrokerAccessTokenCredential]

    @classmethod
    def load(cls) -> "Secrets":
        ...

    @classmethod
    def clean(cls) -> None:
        ...

    def save(self) -> None:
        ...


class FileSecrets(BaseModel):
    id_token: ty.Optional[str] = None
    api_token: ty.Optional[AccessTokenCredential] = None
    broker_tokens: ty.Dict[str, BrokerAccessTokenCredential] = {}

    @classmethod
    def _path(cls) -> Path:
        return config_dir() / "secrets.json"

    @classmethod
    def load(cls) -> "Secrets":
        try:
            return cls.parse_file(cls._path())
        except pydantic.error_wrappers.ValidationError as e:
            raise ProdigyTeamsParseSecretsError(
                secrets_file=cls._path(), error=e
            ) from e
        except FileNotFoundError:
            return cls()

    @classmethod
    def clean(cls) -> None:
        cls._path().unlink(missing_ok=True)

    def save(self) -> None:
        path = self._path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(mode="w", encoding="utf-8") as f:
            try:
                os.fchmod(f.fileno(), 0o600)
            except AttributeError:
                # no chmod on Windows
                pass
            f.write(self.json())


class CLIAuth(ty.Protocol):
    @property
    def client(self) -> Client:
        ...

    @property
    def broker_client(self) -> BrokerClient:
        ...

    @property
    def broker_host(self) -> str:
        ...

    @property
    def broker_url(self) -> URL:
        ...

    @property
    def broker_id(self) -> ty.UUID:
        ...

    @property
    def org_id(self) -> ty.UUID:
        ...

    @property
    def pam_host(self) -> str:
        ...

    @property
    def pam_url(self) -> URL:
        ...

    @property
    def secrets(self) -> Secrets:
        ...

    def retry_id(self, func) -> ty.Callable[..., ty.Any]:
        ...

    def retry_api(self, func) -> ty.Callable[..., ty.Any]:
        ...

    def retry(self, func) -> ty.Callable[..., ty.Any]:
        ...

    def _ensure_readable_secrets(self) -> Secrets:
        ...

    def _ensure_broker_host(self) -> None:
        ...

    def get_id_token(self, force_refresh: bool = False) -> str:
        ...

    def get_api_token(self, force_refresh: bool = False) -> AccessTokenCredential:
        ...

    def get_broker_token(
        self, force_refresh: bool = False
    ) -> BrokerAccessTokenCredential:
        ...


class CLIAuthImpl:
    _pam_url: URL
    _broker_url: ty.Optional[URL]
    _broker_id: ty.Optional[ty.UUID]
    _org_id: ty.Optional[ty.UUID]

    def __init__(self, *, pam_host: str, broker_host: ty.Optional[str]) -> None:
        self._secrets: ty.Optional[Secrets] = None
        self._broker_url = URL.parse(broker_host) if broker_host is not None else None
        self._pam_url = URL.parse(pam_host)
        self._broker_id = None
        self._org_id = None

    @property
    def client(self) -> Client:
        return Client(base_url=self.pam_url.url, token=self.get_api_token())

    @property
    def broker_client(self) -> BrokerClient:
        self._ensure_broker_host()
        return BrokerClient(base_url=self.broker_url.url, token=self.get_broker_token())

    @property
    def broker_host(self) -> str:
        return self.broker_url.netloc

    @property
    def broker_url(self) -> URL:
        assert self._broker_url is not None
        return self._broker_url

    @property
    def broker_id(self) -> ty.UUID:
        if self._broker_id is None:
            if self._broker_url is None:
                raise CLIError(Messages.E035)
            # The models from pam_sdk need to be generated using the default keyword
            # when using pydantic.Field. Pyright needs this to work well
            # Ref: https://pydantic-docs.helpmanual.io/visual_studio_code/#adding-a-default-with-field
            body = BrokerReading(address=str(self.broker_url))  # pyright: ignore
            broker = self.client.broker.read(body)
            self._broker_id = broker.id
        return self._broker_id

    @property
    def org_id(self) -> ty.UUID:
        if self._org_id is None:
            broker = self.client.broker.read(id=self.broker_id)
            self._org_id = broker.org_id
        return self._org_id

    @property
    def pam_host(self) -> str:
        return self.pam_url.netloc

    @property
    def pam_url(self) -> URL:
        # TODO: better error message
        assert self._pam_url is not None
        return self._pam_url

    @property
    def secrets(self) -> Secrets:
        # Secrets are lazy loaded to prevent `ptc login` from crashing due to
        # a broken secrets file.
        if self._secrets is None:
            self._secrets = FileSecrets.load()
        return self._secrets

    def retry_id(self, func) -> ty.Callable[..., ty.Any]:
        def wrapper(*args, **kwargs) -> ty.Any:
            try:
                return func(*args, **kwargs)
            except ProdigyTeamsIDTokenError:
                self.get_id_token(force_refresh=True)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.exception(e)
                    raise CLIError(Messages.E104, e)

        return wrapper

    def retry_api(self, func) -> ty.Callable[..., ty.Any]:
        def wrapper(*args, **kwargs) -> ty.Any:
            try:
                return func(*args, **kwargs)
            except HTTPError:
                self.get_api_token(force_refresh=True)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.exception(e)
                    raise CLIError(Messages.E105, e)

        return wrapper

    def retry(self, func) -> ty.Callable[..., ty.Any]:
        @self.retry_api
        @self.retry_id
        def wrapper(*args, **kwargs) -> ty.Any:
            return func(*args, **kwargs)

        return wrapper

    def _ensure_readable_secrets(self) -> Secrets:
        """Try to load the secrets file, cleaning the file if there is an error"""
        self._secrets = None
        try:
            self.secrets
        except ProdigyTeamsParseSecretsError:
            FileSecrets.clean()
        return self.secrets

    def _ensure_broker_host(self) -> None:
        if self._broker_url is None:
            brokers = self.client.broker.all(size=2)
            if brokers.total == 0:
                raise CLIError(Messages.E106)
            elif brokers.total == 1:
                self._broker_url = URL.parse(brokers.items[0].address)
                SavedSettings.get_and_save("broker_host", self.broker_host)
            else:
                raise CLIError(Messages.E107)

    @staticmethod
    def _check_token_expired(
        token: ty.Union[AccessTokenCredential, BrokerAccessTokenCredential, str]
    ) -> bool:
        # TODO: this is reusing the pam_sdk implementation to reduce duplication
        # in the tricky token management logic. Needs to be cleaned up.
        if isinstance(token, str):
            return AccessTokenCredential(access_token=token).expired
        return token.expired

    def get_id_token(self, force_refresh: bool = False) -> str:
        if (
            self.secrets.id_token is None
            or self._check_token_expired(self.secrets.id_token)
            or force_refresh
        ):
            id_token = self._authenticate_device_and_get_id_token()
            self.secrets.id_token = id_token
            self.secrets.save()
            return id_token
        else:
            return self.secrets.id_token

    def get_api_token(self, force_refresh: bool = False) -> AccessTokenCredential:
        if (
            self.secrets.api_token is None
            or self.secrets.api_token.expired
            or force_refresh
        ):
            id_token = self.get_id_token()
            api_response = httpx.post(
                f"{self.pam_url}/api/v1/login",
                headers={"authorization": f"Bearer {id_token}"},
            )
            if api_response.status_code != 200:
                breakpoint()
                raise ProdigyTeamsIDTokenError()
            data = api_response.json()
            token = AccessTokenCredential(access_token=data["access_token"])
            self.secrets.api_token = token
            self.secrets.save()
            return token
        else:
            return self.secrets.api_token

    def get_broker_token(
        self, force_refresh: bool = False
    ) -> BrokerAccessTokenCredential:
        self._ensure_broker_host()
        if (
            self.broker_host not in self.secrets.broker_tokens
            or self._check_token_expired(self.secrets.broker_tokens[self.broker_host])
            or force_refresh
        ):
            api_token = self.get_api_token().access_token
            res = httpx.post(
                f"{self.broker_url}/api/v1/token",
                headers={"authorization": f"Bearer {api_token}"},
            )
            if res.status_code != 200:
                err = Messages.E034.format(
                    code=res.status_code, reason=res.reason_phrase, url=res.url
                )
                if res.status_code == 401:
                    raise ProdigyTeamsIDTokenError(err)
                raise ProdigyTeamsError(err)
            data = res.json()
            token = BrokerAccessTokenCredential(access_token=data["access_token"])
            self.secrets.broker_tokens[self.broker_host] = token
            self.secrets.save()
            return token
        else:
            return self.secrets.broker_tokens[self.broker_host]

    def _authenticate_device_and_get_id_token(self) -> str:
        try:
            config_response = httpx.get(f"{self.pam_url}/api/v1/cli.json")
            config_response.raise_for_status()
        except Exception as exc:
            err = Messages.E033.format(url=self.pam_url)
            logger.exception(err)
            raise ProdigyTeamsError(err) from exc
        config = config_response.json()
        post_data = {
            "client_id": config["dclient_id"],
            "scope": AUTH0_SCOPE,
            "audience": config["daudience"],
        }
        response = httpx.post(config["dcode_url"], data=post_data)
        if response.status_code != 200:
            error_resp = response.json()
            raise CLIError(Messages.E101, error_resp)
        data = response.json()
        device_code = data.get("device_code")
        user_code = data.get("user_code")
        uri = data.get("verification_uri")
        data.get("expires_in")
        interval = data.get("interval", 5)
        uri_complete = data.get("verification_uri_complete")
        if not (device_code and user_code and uri and interval and uri_complete):
            raise CLIError(Messages.E032, data)
        print_login_info(uri_complete, uri, user_code)
        last_check = 0
        for _ in range(AUTH_WAIT_TIME_SECONDS):
            if time.time() > (last_check + int(interval)):
                token_response = httpx.post(
                    config["dtoken_url"],
                    data={
                        "grant_type": AUTH0_GRANT_TYPE,
                        "device_code": device_code,
                        "client_id": config["dclient_id"],
                    },
                )
                last_check = time.time()
                token_data = token_response.json()
                if token_response.status_code == 200:
                    return token_data.get("id_token")
            time.sleep(1)
        raise ProdigyTeamsIDTokenError(Messages.E031)


AUTH = None


def get_current_auth() -> "CLIAuth":
    """Fetches the current CLI Auth."""
    global AUTH
    if AUTH is None:
        settings = SavedSettings.load()
        if settings.pam_host is None:
            raise CLIError(Messages.E037)
        AUTH = CLIAuthImpl(pam_host=settings.pam_host, broker_host=settings.broker_host)
    return AUTH
