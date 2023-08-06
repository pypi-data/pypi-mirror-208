import json
from typing import IO, Iterator

import httpx

from .. import errors, ty


class RawIteratorIO(IO[bytes]):
    """
    Creates a IO[bytes] from a bytes iterator.

    Adapted from https://stackoverflow.com/a/12604375/7426717
    """

    def __init__(self, it: Iterator[bytes]) -> None:
        self._it = it
        self._memory = b""

        super().__init__()

    def _read1(self, n=None) -> bytes:
        while not self._memory:
            try:
                next_memory = next(self._it)
            except StopIteration:
                break
            else:
                self._memory = next_memory

        chunk = self._memory[:n]
        self._memory = self._memory[len(chunk) :]

        return chunk

    def read(self, n=None) -> bytes:
        chunks = []
        if n is None or n < 0:
            while True:
                m = self._read1()
                if not m:
                    break
                chunks.append(m)
        else:
            while n > 0:
                m = self._read1(n)
                if not m:
                    break
                n -= len(m)
                chunks.append(m)
        return b"".join(chunks)


CHUNK_SIZE = 1024


class BaseClient:
    name: str
    url: str

    def __init__(
        self, sync_client: httpx.Client, async_client: httpx.AsyncClient, path: str
    ) -> None:
        self._sync_client = sync_client
        self._async_client = async_client
        if path.startswith("/"):
            path = path[1:]
        self.name = path.split("/")[-1]
        self.path = f"/{path}"

    def request(
        self,
        method: str,
        *,
        endpoint: str,
        params: ty.Union[None, ty.BaseModel, ty.Dict[str, ty.Any]] = None,
        data: ty.Union[None, ty.BaseModel, ty.Dict[str, ty.Any]] = None,
        files: ty.Optional[ty.Dict[str, ty.Any]] = None,
        headers: ty.Dict[str, str] = {},
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
        params_model: ty.Optional[ty.Type[ty.BaseModel]] = None,
        body_model: ty.Optional[ty.Type[ty.BaseModel]] = None,
        return_model: ty.Optional[ty.Type[ty.BaseModel]] = None,
        stream=False,
    ) -> ty.Union[None, ty.BaseModel, ty.Page[ty.BaseModel], ty.IO[bytes]]:
        req = self._get_validated_request(
            method=method,
            endpoint=endpoint,
            params=params,
            data=data,
            files=files,
            params_model=params_model,
            body_model=body_model,
            headers=headers,
            page=page,
            size=size,
        )
        response = self._sync_client.send(req, stream=stream)
        self._raise_and_handle_errors(response)
        content = None
        if (
            response.headers.get("content-type") == "application/json"
            and response.status_code != 204
        ):
            content = response.json()
        if return_model is not None:
            return self._convert_response_to_model(content, return_model)
        return RawIteratorIO(response.iter_bytes(chunk_size=CHUNK_SIZE))

    async def request_async(
        self,
        method: str,
        *,
        endpoint: str,
        params: ty.Union[None, ty.BaseModel, ty.Dict[str, ty.Any]] = None,
        data: ty.Union[None, ty.BaseModel, ty.Dict[str, ty.Any]] = None,
        files: ty.Optional[ty.Dict[str, ty.Any]] = None,
        headers: ty.Dict[str, str] = {},
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
        params_model: ty.Optional[ty.Type[ty.BaseModel]] = None,
        body_model: ty.Optional[ty.Type[ty.BaseModel]] = None,
        return_model: ty.Optional[ty.Type[ty.BaseModel]] = None,
        stream=True,
    ) -> ty.Union[None, ty.BaseModel, ty.Page[ty.BaseModel], ty.IO]:
        req = self._get_validated_request(
            method=method,
            endpoint=endpoint,
            params=params,
            data=data,
            files=files,
            params_model=params_model,
            body_model=body_model,
            headers=headers,
            page=page,
            size=size,
        )
        response = await self._async_client.send(req, stream=stream)
        self._raise_and_handle_errors(response)
        content = None
        if (
            response.headers.get("content-type") == "application/json"
            and response.status_code != 204
        ):
            content = response.json()
        if return_model is not None:
            return self._convert_response_to_model(content, return_model)
        return RawIteratorIO(response.iter_bytes(CHUNK_SIZE))

    def _get_validated_request(
        self,
        *,
        method: str,
        endpoint: str,
        params: ty.Union[None, ty.BaseModel, ty.Dict[str, ty.Any]] = None,
        data: ty.Union[None, ty.BaseModel, ty.Dict[str, ty.Any]] = None,
        files: ty.Optional[ty.Dict[str, ty.Any]] = None,
        params_model: ty.Optional[ty.Type[ty.BaseModel]] = None,
        body_model: ty.Optional[ty.Type[ty.BaseModel]] = None,
        headers: ty.Optional[ty.Dict[str, str]] = None,
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
    ) -> httpx.Request:
        url = self.path
        if endpoint:
            if endpoint.startswith("/"):
                url = endpoint
            else:
                url = f"{self.path}/{endpoint}"
        local_params = {}
        if page is not None:
            local_params["page"] = page
        if size is not None:
            local_params["size"] = size
        if params is not None:
            if isinstance(params, dict):
                params.update(local_params)
                if params_model is not None:
                    # if params_model is passed, use Pydantic to validate params
                    params = params_model(**params)
                    params = params.dict()
            elif isinstance(params, ty.BaseModel):
                params = params.dict(exclude_none=True, exclude_defaults=True)
                params.update(local_params)
        content = None
        if data is not None:
            if isinstance(data, dict):
                if body_model is not None:
                    body = body_model(**data)
                    content = body.json()
                else:
                    content = json.dumps(data)
            elif isinstance(data, ty.BaseModel):
                content = data.json()
        req = self._sync_client.build_request(
            method, url, headers=headers, params=params, content=content, files=files
        )
        return req

    def _raise_and_handle_errors(self, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            error_type = None
            sdk_error = None
            try:
                error_data = e.response.json()
            except json.JSONDecodeError:
                error_data = {}
            if isinstance(error_data, dict):
                detail = error_data.get("detail")
            else:
                detail = error_data
            if detail and isinstance(detail, dict):
                error_type = detail.get("type")
            if error_type:
                sdk_error = getattr(errors, error_type, None)
            if sdk_error:
                raise sdk_error(detail=json.dumps(detail))
            elif status == 401:
                raise errors.AuthError(detail=json.dumps(detail))
            else:
                raise e

    def _convert_response_to_model(
        self, data: ty.Any, return_model: ty.Type[ty.BaseModel]
    ) -> ty.Union[None, ty.BaseModel, ty.Page[ty.BaseModel]]:
        """Convert the JSON response to the correct Pydantic model"""
        if data is None:
            return data
        return return_model.parse_obj(data)
