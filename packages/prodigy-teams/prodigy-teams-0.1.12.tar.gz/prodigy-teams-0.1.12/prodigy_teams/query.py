import time
from uuid import UUID

from wasabi import msg

from . import ty
from .auth import CLIAuth, get_current_auth
from .config import SavedSettings
from .errors import CLIError, ProdigyTeamsErrors
from .messages import Messages
from .prodigy_teams_broker_sdk import Client as BrokerClient
from .prodigy_teams_broker_sdk import models as broker_models
from .prodigy_teams_pam_sdk import Client as PamClient
from .prodigy_teams_pam_sdk import models as pam_models
from .prodigy_teams_pam_sdk.client.action import Action as PamActionEndpoint
from .prodigy_teams_pam_sdk.client.task import Task as PamTaskEndpoint
from .prodigy_teams_pam_sdk.errors import PRODIGY_TEAMS_ERRORS, ProdigyTeamsError


def get_not_found_error(model_name: str) -> ty.Type[ProdigyTeamsError]:
    name = model_name.title().replace("_", "")
    return PRODIGY_TEAMS_ERRORS[f"{name}NotFound"]


def resolve_action(
    name_or_id: ty.Optional[ty.Union[str, ty.UUID]],
    *,
    broker_id: ty.Optional[ty.UUID],
    project_id: ty.Optional[ty.UUID],
) -> pam_models.ActionReturning:
    if name_or_id is None:
        settings = SavedSettings.load()
        return settings.action  # type: ignore
    return _resolve_object(
        "action", name_or_id, {"broker_id": broker_id, "project_id": project_id}
    )  # type: ignore


def resolve_action_id(
    name_or_id: ty.Optional[ty.Union[str, ty.UUID]],
    *,
    broker_id: ty.Optional[ty.UUID],
    project_id: ty.Optional[ty.UUID],
) -> ty.UUID:
    if name_or_id is None:
        settings = SavedSettings.load()
        return settings.action  # type: ignore
    return _resolve_id(
        "action", name_or_id, {"broker_id": broker_id, "project_id": project_id}
    )  # type: ignore


def resolve_asset(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
    project_id: ty.Optional[ty.UUID],
) -> pam_models.AssetReturning:
    return _resolve_object(
        "asset", name_or_id, {"broker_id": broker_id, "project_id": project_id}
    )  # type: ignore


def resolve_asset_id(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
    project_id: ty.Optional[ty.UUID],
) -> ty.UUID:
    return _resolve_id(
        "asset", name_or_id, {"broker_id": broker_id, "project_id": project_id}
    )


def resolve_broker(
    name_or_id: ty.Union[str, ty.UUID],
) -> pam_models.BrokerReturning:
    return _resolve_object("broker", name_or_id, {})  # type: ignore


def resolve_broker_id(
    name_or_id: ty.Union[str, ty.UUID],
) -> ty.UUID:
    return _resolve_id("broker", name_or_id, {})


def resolve_dataset(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
) -> pam_models.DatasetReturning:
    return _resolve_object("dataset", name_or_id, {"broker_id": broker_id})  # type: ignore


def resolve_dataset_id(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
) -> ty.UUID:
    return _resolve_id("dataset", name_or_id, {"broker_id": broker_id})


def resolve_package(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
) -> pam_models.PackageReturning:
    return _resolve_latest_object(
        "package",
        name_or_id,
        {"broker_id": broker_id},
        pam_models.PackageReadingLatest,
    )  # type: ignore


def resolve_package_id(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
) -> ty.UUID:
    return _resolve_id("package", name_or_id, {"broker_id": broker_id})


def resolve_path(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
) -> pam_models.BrokerPathReturning:
    return _resolve_object("broker_path", name_or_id, {"broker_id": broker_id})  # type: ignore


def resolve_path_id(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
) -> ty.UUID:
    return _resolve_id("broker_path", name_or_id, {"broker_id": broker_id})


def resolve_project(
    name_or_id: ty.Union[str, ty.UUID],
) -> pam_models.ProjectReturning:
    return _resolve_object("project", name_or_id, {})  # type: ignore


def resolve_project_id(
    name_or_id: ty.Union[str, ty.UUID],
) -> ty.UUID:
    return _resolve_id("project", name_or_id, {})


def resolve_recipe(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
) -> pam_models.RecipeDetail:
    return _resolve_latest_object(
        "recipe",
        name_or_id,
        {"broker_id": broker_id},
        pam_models.RecipeReadingLatest,
    )  # type: ignore


# TODO: this is currently not used
def resolve_recipe_id(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
) -> ty.UUID:
    return _resolve_id("recipe", name_or_id, {"broker_id": broker_id})


def resolve_secret(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
) -> pam_models.SecretReturning:
    return _resolve_object("secret", name_or_id, {"broker_id": broker_id})  # type: ignore


def resolve_secret_id(
    name_or_id: ty.Union[str, ty.UUID],
    *,
    broker_id: ty.Optional[ty.UUID],
) -> ty.UUID:
    return _resolve_id("secret", name_or_id, {"broker_id": broker_id})


def resolve_task(
    name_or_id: ty.Optional[ty.Union[str, ty.UUID]],
    *,
    broker_id: ty.Optional[ty.UUID],
    project_id: ty.Optional[ty.UUID],
) -> pam_models.TaskReturning:
    return _resolve_object("task", name_or_id, {"broker_id": broker_id, "project_id": project_id})  # type: ignore


def resolve_task_id(
    name_or_id: ty.Optional[ty.Union[str, ty.UUID]],
    *,
    broker_id: ty.Optional[ty.UUID],
    project_id: ty.Optional[ty.UUID],
) -> ty.UUID:
    return _resolve_id("task", name_or_id, {"broker_id": broker_id, "project_id": project_id})  # type: ignore


def _resolve_id(
    model_name: str,
    name_or_id: ty.Union[str, ty.UUID],
    params: ty.Dict[str, ty.Optional[ty.Union[str, ty.UUID]]],
) -> ty.UUID:
    """Resolve reference to a Prodigy Teams Entity by name or ID.
    If an ID is given, return it. If it's a name,
    look up the ID.
    """
    if isinstance(name_or_id, ty.UUID):
        return name_or_id
    try:
        return UUID(name_or_id)
    except ValueError:
        pass
    auth = get_current_auth()
    model_client = getattr(auth.client, model_name)
    NotFound = get_not_found_error(model_name)
    try:
        res = model_client.read(name=name_or_id, **params)
        return res.id
    except NotFound:
        err = Messages.E038.format(noun=model_name, name_or_id=name_or_id)
        raise CLIError(err, params)


def _resolve_object(
    model_name: str,
    name_or_id: ty.Union[str, ty.UUID],
    params: ty.Dict[str, ty.Optional[ty.Union[str, ty.UUID]]],
) -> ty.BaseModel:
    """Resolve reference to a Prodigy Teams Entity by name or ID.
    If an ID is given, use it for an id query, otherwise, query by
    the entity name
    """
    auth = get_current_auth()
    model_client = getattr(auth.client, model_name)
    NotFound = get_not_found_error(model_name)
    record_id = None
    if isinstance(name_or_id, ty.UUID):
        record_id = name_or_id
    else:
        try:
            record_id = UUID(name_or_id)
        except ValueError:
            pass
    if record_id:
        try:
            res = model_client.read(id=record_id, **params)
        except NotFound:
            err = Messages.E038.format(noun=model_name, name_or_id=name_or_id)
            raise CLIError(err, params)
    else:
        try:
            res = model_client.read(name=name_or_id, **params)
        except NotFound:
            err = Messages.E038.format(noun=model_name, name_or_id=name_or_id)
            raise CLIError(err, params)
    return res


def _resolve_latest_object(
    model_name: str,
    name_or_id: ty.Union[str, ty.UUID],
    params: ty.Dict[str, ty.Optional[ty.Union[str, ty.UUID]]],
    latest_request_model: ty.Type[pam_models.BaseModel],
) -> pam_models.BaseModel:
    """Resolve latest reference to a Prodigy Teams Entity by name or ID.
    If an ID is given, use it for an id query, otherwise, query by
    the entity name
    """
    auth = get_current_auth()
    model_client = getattr(auth.client, model_name)
    NotFound = get_not_found_error(model_name)
    record_id = None
    if isinstance(name_or_id, ty.UUID):
        record_id = name_or_id
    else:
        try:
            record_id = UUID(name_or_id)
        except ValueError:
            pass
    if record_id:
        try:
            res = model_client.read(id=record_id, **params)
        except NotFound:
            err = Messages.E038.format(noun=model_name, name_or_id=name_or_id)
            raise CLIError(err, params)
    else:
        body = latest_request_model(name=name_or_id, **params)
        try:
            res = model_client.latest(body=body)
        except NotFound:
            err = Messages.E038.format(
                noun=model_name, name_or_id=getattr(body, "name", None)
            )
            raise CLIError(err, body)
    return res


class JobOperations:
    def __init__(
        self,
        pam_client: PamClient,
        broker_client: BrokerClient,
        job_type: ty.Literal["task", "action"],
    ) -> None:
        self.pam_client = pam_client
        self.broker_client = broker_client
        self.job_type = broker_models.JobType(job_type)

    def start(self, job_id: ty.UUID) -> None:
        change_response = self.broker_client.jobs.start_job(
            broker_models.JobID(id=job_id, job_type=self.job_type)
        )
        if change_response.nomad_change is not None:
            return
        elif change_response.nomad_error:
            err = Messages.E025.format(noun=self.job_type.value, name=job_id)
            raise CLIError(err, change_response.nomad_error)
        elif not change_response.pam_error and not change_response.validation_error:
            msg.info(Messages.T006.format(noun=self.job_type.value, name=job_id))

    def stop(self, job_id: ty.UUID) -> None:
        change_response = self.broker_client.jobs.stop_job(
            broker_models.JobID(id=job_id, job_type=self.job_type)
        )
        if change_response.nomad_change is not None:
            msg.good(Messages.T007.format(noun=self.job_type.value, name=job_id))
        elif change_response.nomad_error:
            err = Messages.E026.format(noun=self.job_type.value, name=job_id)
            raise CLIError(err, change_response.nomad_error)
        elif not change_response.pam_error and not change_response.validation_error:
            msg.info(Messages.T008.format(noun=self.job_type.value, name=job_id))

    def delete(self, job_id: ty.UUID) -> None:
        change_response = self.broker_client.jobs.stop_job(
            broker_models.JobID(id=job_id, job_type=self.job_type)
        )
        if change_response.pam_error is not None:
            raise CLIError(Messages.E027.format(noun=self.job_type.value, name=job_id))
        elif change_response.nomad_error:
            err = Messages.E028.format(noun=self.job_type.value, name=job_id)
            raise CLIError(err, change_response.nomad_error)
        else:
            msg.good(Messages.T009.format(noun=self.job_type.value, name=job_id))
        try:
            self.pam_endpoint().delete(id=job_id)
        except (ProdigyTeamsErrors.TaskNotFound, ProdigyTeamsErrors.ActionNotFound):
            raise CLIError(Messages.E029.format(noun=self.job_type.value, name=job_id))
        except (
            ProdigyTeamsErrors.TaskForbiddenDelete,
            ProdigyTeamsErrors.TaskForbiddenRead,
            ProdigyTeamsErrors.ActionForbiddenDelete,
            ProdigyTeamsErrors.ActionForbiddenRead,
        ):
            raise CLIError(Messages.E030.format(noun=self.job_type.value, name=job_id))
        msg.good(Messages.T003.format(noun=self.job_type.value, name=job_id))

    def pam_endpoint(self) -> ty.Union[PamActionEndpoint, PamTaskEndpoint]:
        return getattr(self.pam_client, self.job_type.value)


_JobT = ty.TypeVar(
    "_JobT", bound=ty.Union[pam_models.TaskReturning, pam_models.ActionReturning]
)


def start_job(job: _JobT, auth: CLIAuth) -> _JobT:
    job_type = "task" if isinstance(job, pam_models.TaskReturning) else "action"
    job_operations = JobOperations(auth.client, auth.broker_client, job_type)
    job_operations.start(job.id)
    SavedSettings.get_and_save(job_type, job.id)
    res = check_job_started(job)
    if res is not None:
        print(res.url)
    return job


def stop_job(job: _JobT, auth: CLIAuth) -> _JobT:
    job_type = "task" if isinstance(job, pam_models.TaskReturning) else "action"
    job_operations = JobOperations(auth.client, auth.broker_client, job_type)
    job_operations.stop(job.id)
    SavedSettings.get_and_save(job_type, job.id)
    return job


def delete_job(job: _JobT, auth: CLIAuth) -> _JobT:
    job_type = "task" if isinstance(job, pam_models.TaskReturning) else "action"
    job_operations = JobOperations(auth.client, auth.broker_client, job_type)
    job_operations.delete(job.id)
    SavedSettings.get_and_save(job_type, None)
    return job


def check_job_started(job: _JobT, *, wait_seconds: int = 60 * 2) -> ty.Optional[_JobT]:
    res = job
    if res.is_running:
        return job
    job_type = "task" if isinstance(job, pam_models.TaskReturning) else "action"
    failed_states = [pam_models.TaskState.FAILED, pam_models.ActionState.FAILED]
    resolver = resolve_task if job_type == "task" else resolve_action
    with msg.loading(Messages.T034.format(noun=job_type)):
        for _ in range(wait_seconds):
            res = resolver(job.id, broker_id=job.broker_id, project_id=job.project_id)
            if res.is_running or res.error is not None or res.state in failed_states:
                break
            time.sleep(1)
    if res.is_running:
        msg.good(Messages.T005.format(noun=job_type, name=job.id))
        return res
    elif res.error is not None or res.state in failed_states:
        raise CLIError(Messages.E025.format(noun=job_type, name=job.id), res.url_logs)
    msg.warn(Messages.E025.format(noun=job_type, name=job.id), res.url_logs)


def collect_from_pages(request: ty.Callable[[int], ty.Page]) -> ty.Iterable[ty.Page]:
    page = 1
    while True:
        page_result = request(page)

        if page_result.items:
            yield page_result
        else:
            break

        page += 1
