from pathlib import Path

from pydantic import BaseModel

from . import ty
from .util import APP_NAME, get_app_dir


def config_dir() -> Path:
    return Path(get_app_dir(APP_NAME))


class SavedSettings(BaseModel):
    broker_host: ty.Optional[str]
    project: ty.Optional[ty.UUID]
    task: ty.Optional[ty.UUID]
    action: ty.Optional[ty.UUID]
    pam_host: ty.Optional[str]

    @classmethod
    def _path(cls) -> Path:
        return config_dir() / "saved-defaults.json"

    @classmethod
    def blank(cls) -> "SavedSettings":
        return cls(
            broker_host=None, project=None, task=None, action=None, pam_host=None
        )

    @classmethod
    def load(cls) -> "SavedSettings":
        try:
            return cls.parse_file(cls._path())
        except FileNotFoundError:
            return cls.blank()

    def reset_defaults(self) -> None:
        """Reset defaut project/task/action, e.g. on host changes."""
        self.project = None
        self.task = None
        self.action = None

    def to_json(self) -> ty.JSONableDict:
        data = {}
        for key, value in self.dict().items():
            # UUIDs are not JSON-seriazliable by default
            data[key] = str(value) if isinstance(value, ty.UUID) else value
        return data

    def save(self) -> None:
        path = self._path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.json(), encoding="utf-8")

    @ty.overload
    def get(self, field: ty.Literal["broker_host", "pam_host"]) -> str:
        ...

    @ty.overload
    def get(self, field: ty.Literal["project", "task", "action"]) -> str:
        ...

    def get(
        self, field: ty.Literal["broker_host", "pam_host", "project", "task", "action"]
    ) -> ty.Union[str, ty.UUID]:
        return getattr(self, field)

    @ty.overload
    @classmethod
    def get_and_save(
        cls,
        field: ty.Literal["broker_host", "pam_host"],
        override: ty.Optional[str] = None,
    ) -> str:
        ...

    @ty.overload
    @classmethod
    def get_and_save(
        cls,
        field: ty.Literal["project", "task", "action"],
        override: ty.Optional[ty.UUID] = None,
    ) -> ty.UUID:
        ...

    @classmethod
    def get_and_save(
        cls,
        field: ty.Literal["broker_host", "pam_host", "project", "task", "action"],
        override: ty.Optional[ty.Union[str, ty.UUID]] = None,
    ) -> ty.Union[str, ty.UUID]:
        settings = cls.load()
        if override is None:
            return getattr(settings, field)
        else:
            setattr(settings, field, override)
            if field in ["broker_host", "pam_host"]:
                settings.reset_defaults()
            settings.save()
            return override
