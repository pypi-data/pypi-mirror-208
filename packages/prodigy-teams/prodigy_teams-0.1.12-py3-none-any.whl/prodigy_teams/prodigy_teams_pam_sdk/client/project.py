from ..models import (
    ProjectCreating,
    ProjectDeleting,
    ProjectReading,
    ProjectReturning,
    ProjectUpdating,
)
from .base import ModelClient


class Project(
    ModelClient[
        ProjectCreating,
        ProjectReading,
        ProjectUpdating,
        ProjectDeleting,
        ProjectReturning,
        ProjectReturning,
    ]
):
    Creating = ProjectCreating
    Reading = ProjectReading
    Updating = ProjectUpdating
    Deleting = ProjectDeleting
    Returning = ProjectReturning
