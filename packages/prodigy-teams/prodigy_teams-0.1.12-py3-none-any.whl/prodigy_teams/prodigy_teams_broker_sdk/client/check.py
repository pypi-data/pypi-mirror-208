from .. import ty
from ..models import (
    CheckProgressRequest,
    CheckProgressResponse,
    CheckStartRequest,
    CheckStartResponse,
)
from .base import BaseClient


class Check(BaseClient):
    def start(self, body: CheckStartRequest) -> CheckStartResponse:
        res = self.request(
            "POST", endpoint="start", data=body, return_model=CheckStartResponse
        )
        return ty.cast(CheckStartResponse, res)

    async def start_async(self, body: CheckStartRequest) -> CheckStartResponse:
        res = await self.request_async(
            "POST", endpoint="start", data=body, return_model=CheckStartResponse
        )
        return ty.cast(CheckStartResponse, res)

    def progress(self, body: CheckProgressRequest) -> CheckProgressResponse:
        res = self.request(
            "POST", endpoint="progress", data=body, return_model=CheckProgressResponse
        )
        return ty.cast(CheckProgressResponse, res)

    async def progress_async(self, body: CheckProgressRequest) -> CheckProgressResponse:
        res = await self.request_async(
            "POST", endpoint="progress", data=body, return_model=CheckProgressResponse
        )
        return ty.cast(CheckProgressResponse, res)
