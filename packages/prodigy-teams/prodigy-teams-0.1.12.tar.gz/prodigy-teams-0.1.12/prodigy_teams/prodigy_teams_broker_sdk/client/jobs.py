from .. import ty
from ..models import (
    JobActionResponse,
    JobID,
    JobLogRequest,
    JobLogResponse,
    TasksBaseUrl,
)
from .base import BaseClient


class Jobs(BaseClient):
    def get_base_url(self) -> TasksBaseUrl:
        res = self.request("POST", endpoint="get-base-url", return_model=TasksBaseUrl)
        return ty.cast(TasksBaseUrl, res)

    async def get_base_url_async(self) -> TasksBaseUrl:
        res = await self.request_async(
            "POST", endpoint="get-base-url", return_model=TasksBaseUrl
        )
        return ty.cast(TasksBaseUrl, res)

    def start_job(self, body: JobID) -> JobActionResponse:
        res = self.request(
            "POST", endpoint="start-job", data=body, return_model=JobActionResponse
        )
        return ty.cast(JobActionResponse, res)

    async def start_job_async(self, body: JobID) -> JobActionResponse:
        res = await self.request_async(
            "POST", endpoint="start-job", data=body, return_model=JobActionResponse
        )
        return ty.cast(JobActionResponse, res)

    def stop_job(self, body: JobID) -> JobActionResponse:
        res = self.request(
            "POST", endpoint="stop-job", data=body, return_model=JobActionResponse
        )
        return ty.cast(JobActionResponse, res)

    async def stop_job_async(self, body: JobID) -> JobActionResponse:
        res = await self.request_async(
            "POST", endpoint="stop-job", data=body, return_model=JobActionResponse
        )
        return ty.cast(JobActionResponse, res)

    def delete_job(self, body: JobID) -> JobActionResponse:
        res = self.request(
            "POST", endpoint="delete-job", data=body, return_model=JobActionResponse
        )
        return ty.cast(JobActionResponse, res)

    async def delete_job_async(self, body: JobID) -> JobActionResponse:
        res = await self.request_async(
            "POST", endpoint="delete-job", data=body, return_model=JobActionResponse
        )
        return ty.cast(JobActionResponse, res)

    def logs(self, body: JobLogRequest) -> JobLogResponse:
        res = self.request(
            "POST", endpoint="logs", data=body, return_model=JobLogResponse
        )
        return ty.cast(JobLogResponse, res)

    async def logs_async(self, body: JobLogRequest) -> JobLogResponse:
        res = await self.request_async(
            "POST", endpoint="logs", data=body, return_model=JobLogResponse
        )
        return ty.cast(JobLogResponse, res)
