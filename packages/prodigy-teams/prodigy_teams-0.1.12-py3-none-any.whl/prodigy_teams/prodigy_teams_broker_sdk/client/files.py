from .. import ty
from ..models import (
    Copying,
    CopyPlan,
    Deleting,
    Downloading,
    FileStats,
    Listing,
    PathList,
    RsyncPlan,
    Statting,
)
from .base import BaseClient


class Files(BaseClient):
    def upload(
        self, file: ty.IO, *, dest: str, overwrite: bool, make_dirs: bool
    ) -> None:
        res = self.request(
            "POST",
            endpoint="upload",
            files={"file": file},
            params={"dest": dest, "overwrite": overwrite, "make_dirs": make_dirs},
            return_model=None,
        )
        return ty.cast(None, res)

    async def upload_async(
        self, file: ty.IO, *, dest: str, overwrite: bool, make_dirs: bool
    ) -> None:
        res = await self.request_async(
            "POST",
            endpoint="upload",
            files={"file": file},
            params={"dest": dest, "overwrite": overwrite, "make_dirs": make_dirs},
            return_model=None,
        )
        return ty.cast(None, res)

    def copy(self, body: Copying) -> None:
        res = self.request("POST", endpoint="copy", data=body, return_model=None)
        return ty.cast(None, res)

    async def copy_async(self, body: Copying) -> None:
        res = await self.request_async(
            "POST", endpoint="copy", data=body, return_model=None
        )
        return ty.cast(None, res)

    def delete(self, body: Deleting) -> None:
        res = self.request("POST", endpoint="delete", data=body, return_model=None)
        return ty.cast(None, res)

    async def delete_async(self, body: Deleting) -> None:
        res = await self.request_async(
            "POST", endpoint="delete", data=body, return_model=None
        )
        return ty.cast(None, res)

    def stat(self, body: Statting) -> FileStats:
        res = self.request("POST", endpoint="stat", data=body, return_model=FileStats)
        return ty.cast(FileStats, res)

    async def stat_async(self, body: Statting) -> FileStats:
        res = await self.request_async(
            "POST", endpoint="stat", data=body, return_model=FileStats
        )
        return ty.cast(FileStats, res)

    def list_dir(self, body: Listing) -> PathList:
        res = self.request(
            "POST", endpoint="list-dir", data=body, return_model=PathList
        )
        return ty.cast(PathList, res)

    async def list_dir_async(self, body: Listing) -> PathList:
        res = await self.request_async(
            "POST", endpoint="list-dir", data=body, return_model=PathList
        )
        return ty.cast(PathList, res)

    def plan_directory_copy(self, body: Copying) -> CopyPlan:
        res = self.request(
            "POST", endpoint="plan-directory-copy", data=body, return_model=CopyPlan
        )
        return ty.cast(CopyPlan, res)

    async def plan_directory_copy_async(self, body: Copying) -> CopyPlan:
        res = await self.request_async(
            "POST", endpoint="plan-directory-copy", data=body, return_model=CopyPlan
        )
        return ty.cast(CopyPlan, res)

    def plan_directory_rsync(self, body: Copying) -> RsyncPlan:
        res = self.request(
            "POST", endpoint="plan-directory-rsync", data=body, return_model=CopyPlan
        )
        return ty.cast(RsyncPlan, res)

    async def plan_directory_rsync_async(self, body: Copying) -> RsyncPlan:
        res = await self.request_async(
            "POST", endpoint="plan-directory-rsync", data=body, return_model=CopyPlan
        )
        return ty.cast(RsyncPlan, res)

    def download(self, body: Downloading) -> ty.IO:  # StreamingResponse
        res = self.request("POST", endpoint="download", data=body, stream=True)
        return ty.cast(ty.IO, res)

    async def download_async(self, body: Downloading) -> ty.IO:
        res = await self.request_async(
            "POST", endpoint="download", data=body, stream=True
        )
        return ty.cast(ty.IO, res)
