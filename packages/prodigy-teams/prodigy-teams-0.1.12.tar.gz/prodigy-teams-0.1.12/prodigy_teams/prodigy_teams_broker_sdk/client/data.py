from .. import ty
from ..models import Dataset, DatasetCreating, DatasetQueryResponse
from .base import BaseClient


class Data(BaseClient):
    def all(
        self,
        session: ty.Optional[bool] = None,
        *,
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
    ) -> ty.Page[str]:
        res = self.request(
            "GET",
            endpoint="all",
            data={"session": session},
            page=page,
            size=size,
            return_model=ty.Page[str],
        )
        return ty.cast(ty.Page[str], res)

    async def all_async(
        self,
        session: ty.Optional[bool] = None,
        *,
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
    ) -> ty.Page[str]:
        res = await self.request_async(
            "GET",
            endpoint="all",
            data={"session": session},
            page=page,
            size=size,
            return_model=ty.Page[str],
        )
        return ty.cast(ty.Page[str], res)

    def create(self, body: DatasetCreating) -> Dataset:
        res = self.request("POST", endpoint="create", data=body, return_model=Dataset)
        return ty.cast(Dataset, res)

    async def create_async(self, body: DatasetCreating) -> Dataset:
        res = await self.request_async(
            "POST", endpoint="create", data=body, return_model=Dataset
        )
        return ty.cast(Dataset, res)

    def read_examples(
        self,
        name: str,
        *,
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
    ) -> DatasetQueryResponse:
        params: dict = {
            "name": name,
        }
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size

        res = self.request(
            "GET",
            endpoint="read-examples",
            params=params,
            return_model=DatasetQueryResponse,
        )
        return ty.cast(DatasetQueryResponse, res)

    async def read_examples_async(
        self,
        name: str,
        *,
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
    ) -> DatasetQueryResponse:
        params: dict = {
            "name": name,
        }
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size

        res = await self.request_async(
            "GET",
            endpoint="read-examples",
            params=params,
            return_model=DatasetQueryResponse,
        )
        return ty.cast(DatasetQueryResponse, res)
