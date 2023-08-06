from . import ty


class ProdigyTeamsError(Exception):
    def __init__(
        self,
        message: ty.Optional[str] = None,
        detail: ty.Optional[str] = None,
        status: ty.Optional[int] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__()
        self.message = message
        self.detail = detail
        self.status = status
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:
        output = ""
        if self.message:
            output = self.message
        if self.detail:
            output += f"\n{self.detail}" if output else self.detail
        return output


class RecipeProcessingError(Exception):
    def __init__(self, title: str, text: ty.Optional[ty.Any] = None) -> None:
        self.title = title
        self.text = text
        self.message = self.title + (f"\n{self.text}" if self.text else "")
        super().__init__(self.message)


class BaseCRUDError(ProdigyTeamsError):
    """Base class that can be changed per project."""


class Invalid(BaseCRUDError):
    pass


class NotFound(BaseCRUDError):
    pass


class Exists(BaseCRUDError):
    pass


class Forbidden(BaseCRUDError):
    pass


class Unsupported(BaseCRUDError):
    pass


class ForbiddenCreate(Forbidden):
    pass


class ForbiddenRead(Forbidden):
    pass


class ForbiddenUpdate(Forbidden):
    pass


class ForbiddenDelete(Forbidden):
    pass


class AuthError(ProdigyTeamsError):
    def __init__(self, detail: str = "Auth Error"):
        self.status = 401
        self.detail = detail

    def __str__(self):
        return self.detail


class AssetNotFound(NotFound):
    pass


class AssetInvalid(Invalid):
    pass


class AssetExists(Exists):
    pass


class AssetForbiddenCreate(ForbiddenCreate):
    pass


class AssetForbiddenRead(ForbiddenRead):
    pass


class AssetForbiddenUpdate(ForbiddenUpdate):
    pass


class AssetForbiddenDelete(ForbiddenDelete):
    pass


class AssetUnsupported(Unsupported):
    pass


class EnvironmentNotFound(NotFound):
    pass


class EnvironmentInvalid(Invalid):
    pass


class EnvironmentExists(Exists):
    pass


class EnvironmentForbiddenCreate(ForbiddenCreate):
    pass


class EnvironmentForbiddenRead(ForbiddenRead):
    pass


class EnvironmentForbiddenUpdate(ForbiddenUpdate):
    pass


class EnvironmentForbiddenDelete(ForbiddenDelete):
    pass


class EnvironmentUnsupported(Unsupported):
    pass


class GroupNotFound(NotFound):
    pass


class GroupInvalid(Invalid):
    pass


class GroupExists(Exists):
    pass


class GroupForbiddenCreate(ForbiddenCreate):
    pass


class GroupForbiddenRead(ForbiddenRead):
    pass


class GroupForbiddenUpdate(ForbiddenUpdate):
    pass


class GroupForbiddenDelete(ForbiddenDelete):
    pass


class GroupUnsupported(Unsupported):
    pass


class BrokerRegistrationNotFound(NotFound):
    pass


class BrokerRegistrationInvalid(Invalid):
    pass


class BrokerRegistrationExists(Exists):
    pass


class BrokerRegistrationForbiddenCreate(ForbiddenCreate):
    pass


class BrokerRegistrationForbiddenRead(ForbiddenRead):
    pass


class BrokerRegistrationForbiddenUpdate(ForbiddenUpdate):
    pass


class BrokerRegistrationForbiddenDelete(ForbiddenDelete):
    pass


class BrokerRegistrationUnsupported(Unsupported):
    pass


class BrokerNotFound(NotFound):
    pass


class BrokerInvalid(Invalid):
    pass


class BrokerExists(Exists):
    pass


class BrokerForbiddenCreate(ForbiddenCreate):
    pass


class BrokerForbiddenRead(ForbiddenRead):
    pass


class BrokerForbiddenUpdate(ForbiddenUpdate):
    pass


class BrokerForbiddenDelete(ForbiddenDelete):
    pass


class BrokerUnsupported(Unsupported):
    pass


class BrokerPathNotFound(NotFound):
    pass


class BrokerPathInvalid(Invalid):
    pass


class BrokerPathExists(Exists):
    pass


class BrokerPathForbiddenCreate(ForbiddenCreate):
    pass


class BrokerPathForbiddenRead(ForbiddenRead):
    pass


class BrokerPathForbiddenUpdate(ForbiddenUpdate):
    pass


class BrokerPathForbiddenDelete(ForbiddenDelete):
    pass


class BrokerPathUnsupported(Unsupported):
    pass


class OrgNotFound(NotFound):
    pass


class OrgInvalid(Invalid):
    pass


class OrgExists(Exists):
    pass


class OrgForbiddenCreate(ForbiddenCreate):
    pass


class OrgForbiddenRead(ForbiddenRead):
    pass


class OrgForbiddenUpdate(ForbiddenUpdate):
    pass


class OrgForbiddenDelete(ForbiddenDelete):
    pass


class OrgUnsupported(Unsupported):
    pass


class PackageNotFound(NotFound):
    pass


class PackageInvalid(Invalid):
    pass


class PackageExists(Exists):
    pass


class PackageForbiddenCreate(ForbiddenCreate):
    pass


class PackageForbiddenRead(ForbiddenRead):
    pass


class PackageForbiddenUpdate(ForbiddenUpdate):
    pass


class PackageForbiddenDelete(ForbiddenDelete):
    pass


class PackageForbiddenDeleteForExistingPlans(PackageForbiddenDelete):
    pass


class PackageUnsupported(Unsupported):
    pass


class PersonNotFound(NotFound):
    pass


class PersonInvalid(Invalid):
    pass


class PersonExists(Exists):
    pass


class PersonForbiddenCreate(ForbiddenCreate):
    pass


class PersonForbiddenRead(ForbiddenRead):
    pass


class PersonForbiddenUpdate(ForbiddenUpdate):
    pass


class PersonForbiddenDelete(ForbiddenDelete):
    pass


class PersonUnsupported(Unsupported):
    pass


class ProjectNotFound(NotFound):
    pass


class ProjectInvalid(Invalid):
    pass


class ProjectExists(Exists):
    pass


class ProjectForbiddenCreate(ForbiddenCreate):
    pass


class ProjectForbiddenRead(ForbiddenRead):
    pass


class ProjectForbiddenUpdate(ForbiddenUpdate):
    pass


class ProjectForbiddenDelete(ForbiddenDelete):
    pass


class ProjectUnsupported(Unsupported):
    pass


class RecipeNotFound(NotFound):
    pass


class RecipeInvalid(Invalid):
    pass


class RecipeExists(Exists):
    pass


class RecipeForbiddenCreate(ForbiddenCreate):
    pass


class RecipeForbiddenRead(ForbiddenRead):
    pass


class RecipeForbiddenUpdate(ForbiddenUpdate):
    pass


class RecipeForbiddenDelete(ForbiddenDelete):
    pass


class RecipeUnsupported(Unsupported):
    pass


class Recipe_AmbiguousReference(Invalid):
    pass


class RequirementsGroupNotFound(NotFound):
    pass


class RequirementsGroupInvalid(Invalid):
    pass


class RequirementsGroupExists(Exists):
    pass


class RequirementsGroupForbiddenCreate(ForbiddenCreate):
    pass


class RequirementsGroupForbiddenRead(ForbiddenRead):
    pass


class RequirementsGroupForbiddenUpdate(ForbiddenUpdate):
    pass


class RequirementsGroupForbiddenDelete(ForbiddenDelete):
    pass


class RequirementsGroupUnsupported(Unsupported):
    pass


class InvitationNotFound(NotFound):
    pass


class InvitationInvalid(Invalid):
    pass


class InvitationExists(Exists):
    pass


class InvitationForbiddenCreate(ForbiddenCreate):
    pass


class InvitationForbiddenRead(ForbiddenRead):
    pass


class InvitationForbiddenUpdate(ForbiddenUpdate):
    pass


class InvitationForbiddenDelete(ForbiddenDelete):
    pass


class InvitationUnsupported(Unsupported):
    pass


class JobPlanNotFound(NotFound):
    pass


class JobPlanInvalid(Invalid):
    pass


class JobPlanExists(Exists):
    pass


class JobPlanForbiddenCreate(ForbiddenCreate):
    pass


class JobPlanForbiddenRead(ForbiddenRead):
    pass


class JobPlanForbiddenUpdate(ForbiddenUpdate):
    pass


class JobPlanForbiddenDelete(ForbiddenDelete):
    pass


class JobPlanUnsupported(Unsupported):
    pass


class JobArgNotFound(NotFound):
    pass


class JobArgInvalid(Invalid):
    pass


class JobArgExists(Exists):
    pass


class JobArgForbiddenCreate(ForbiddenCreate):
    pass


class JobArgForbiddenRead(ForbiddenRead):
    pass


class JobArgForbiddenUpdate(ForbiddenUpdate):
    pass


class JobArgForbiddenDelete(ForbiddenDelete):
    pass


class JobArgUnsupported(Unsupported):
    pass


class NomadAttempt_Invalid(Invalid):
    pass


class NomadAttempt_NotFound(NotFound):
    pass


class NomadAttempt_Exists(Exists):
    pass


class NomadAttempt_ForbiddenCreate(ForbiddenCreate):
    pass


class NomadAttempt_ForbiddenRead(ForbiddenRead):
    pass


class NomadAttempt_ForbiddenUpdate(ForbiddenUpdate):
    pass


class NomadAttempt_ForbiddenDelete(ForbiddenDelete):
    pass


class NomadAttempt_Unsupported(Unsupported):
    pass


class NomadEvent_Invalid(Invalid):
    pass


class NomadEvent_NotFound(NotFound):
    pass


class NomadEvent_Exists(Exists):
    pass


class NomadEvent_ForbiddenCreate(ForbiddenCreate):
    pass


class NomadEvent_ForbiddenRead(ForbiddenRead):
    pass


class NomadEvent_ForbiddenUpdate(ForbiddenUpdate):
    pass


class NomadEvent_ForbiddenDelete(ForbiddenDelete):
    pass


class NomadEvent_Unsupported(Unsupported):
    pass


class Notification_Invalid(Invalid):
    pass


class Notification_NotFound(NotFound):
    pass


class Notification_Exists(Exists):
    pass


class NotificationNotFound(NotFound):
    pass


class NotificationInvalid(Invalid):
    pass


class NotificationExists(Exists):
    pass


class NotificationForbiddenCreate(ForbiddenCreate):
    pass


class NotificationForbiddenRead(ForbiddenRead):
    pass


class NotificationForbiddenUpdate(ForbiddenUpdate):
    pass


class NotificationForbiddenDelete(ForbiddenDelete):
    pass


class NotificationUnsupported(Unsupported):
    pass


class TaskNotFound(NotFound):
    pass


class TaskInvalid(Invalid):
    pass


class TaskExists(Exists):
    pass


class TaskForbiddenCreate(ForbiddenCreate):
    pass


class TaskForbiddenRead(ForbiddenRead):
    pass


class TaskForbiddenUpdate(ForbiddenUpdate):
    pass


class TaskForbiddenDelete(ForbiddenDelete):
    pass


class TaskUnsupported(Unsupported):
    pass


class ActionNotFound(NotFound):
    pass


class ActionInvalid(Invalid):
    pass


class ActionExists(Exists):
    pass


class ActionForbiddenCreate(ForbiddenCreate):
    pass


class ActionForbiddenRead(ForbiddenRead):
    pass


class ActionForbiddenUpdate(ForbiddenUpdate):
    pass


class ActionForbiddenDelete(ForbiddenDelete):
    pass


class ActionUnsupported(Unsupported):
    pass


class UserNotFound(NotFound):
    pass


class UserInvalid(Invalid):
    pass


class UserExists(Exists):
    pass


class UserForbiddenCreate(ForbiddenCreate):
    pass


class UserForbiddenRead(ForbiddenRead):
    pass


class UserForbiddenUpdate(ForbiddenUpdate):
    pass


class UserForbiddenDelete(ForbiddenDelete):
    pass


class UserUnsupported(Unsupported):
    pass


class SessionNotFound(NotFound):
    pass


class SessionInvalid(Invalid):
    pass


class SessionExists(Exists):
    pass


class SessionForbiddenCreate(ForbiddenCreate):
    pass


class SessionForbiddenRead(ForbiddenRead):
    pass


class SessionForbiddenUpdate(ForbiddenUpdate):
    pass


class SessionForbiddenDelete(ForbiddenDelete):
    pass


class SessionUnsupported(Unsupported):
    pass


class DatasetNotFound(NotFound):
    pass


class DatasetInvalid(Invalid):
    pass


class DatasetExists(Exists):
    pass


class DatasetForbiddenCreate(ForbiddenCreate):
    pass


class DatasetForbiddenRead(ForbiddenRead):
    pass


class DatasetForbiddenUpdate(ForbiddenUpdate):
    pass


class DatasetForbiddenDelete(ForbiddenDelete):
    pass


class DatasetUnsupported(Unsupported):
    pass


class SecretNotFound(NotFound):
    pass


class SecretInvalid(Invalid):
    pass


class SecretExists(Exists):
    pass


class SecretForbiddenCreate(ForbiddenCreate):
    pass


class SecretForbiddenRead(ForbiddenRead):
    pass


class SecretForbiddenUpdate(ForbiddenUpdate):
    pass


class SecretForbiddenDelete(ForbiddenDelete):
    pass


class SecretUnsupported(Unsupported):
    pass


PRODIGY_TEAMS_ERRORS = {
    k: v
    for k, v in globals().items()
    if type(v) is type and issubclass(v, ProdigyTeamsError)
}
