import json

import httpx
from pydantic import BaseModel

from .. import errors, ty


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
        endpoint: ty.Optional[str] = None,
        params: ty.Union[None, BaseModel, ty.Dict[str, ty.Any]] = None,
        data: ty.Union[None, BaseModel, ty.Dict[str, ty.Any]] = None,
        headers: ty.Dict[str, str] = {},
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
        params_model: ty.Optional[ty.Type[BaseModel]] = None,
        body_model: ty.Optional[ty.Type[BaseModel]] = None,
        return_model: ty.Optional[ty.Type[BaseModel]] = None,
    ) -> ty.Union[None, BaseModel, ty.Page[BaseModel]]:
        req = self._get_validated_request(
            method=method,
            endpoint=endpoint or "",
            params=params,
            data=data,
            params_model=params_model,
            body_model=body_model,
            headers=headers,
            page=page,
            size=size,
        )
        response = self._sync_client.send(req)
        self._raise_and_handle_errors(response)
        content = None
        if response.content:
            content = response.json()
        if return_model is not None:
            return self._convert_response_to_model(content, return_model)

    async def request_async(
        self,
        method: str,
        *,
        endpoint: ty.Optional[str] = None,
        params: ty.Union[None, BaseModel, ty.Dict[str, ty.Any]] = None,
        data: ty.Union[None, BaseModel, ty.Dict[str, ty.Any]] = None,
        headers: ty.Dict[str, str] = {},
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
        params_model: ty.Optional[ty.Type[BaseModel]] = None,
        body_model: ty.Optional[ty.Type[BaseModel]] = None,
        return_model: ty.Optional[ty.Type[BaseModel]] = None,
    ) -> ty.Union[None, BaseModel, ty.Page[BaseModel]]:
        req = self._get_validated_request(
            method=method,
            endpoint=endpoint or "",
            params=params,
            data=data,
            params_model=params_model,
            body_model=body_model,
            headers=headers,
            page=page,
            size=size,
        )
        response = await self._async_client.send(req)
        self._raise_and_handle_errors(response)
        content = None
        if response.content:
            content = response.json()
        if return_model is not None:
            return self._convert_response_to_model(content, return_model)

    def _get_validated_request(
        self,
        *,
        method: str,
        endpoint: str,
        params: ty.Union[None, BaseModel, ty.Dict[str, ty.Any]] = None,
        data: ty.Union[None, BaseModel, ty.Dict[str, ty.Any]] = None,
        params_model: ty.Optional[ty.Type[BaseModel]] = None,
        body_model: ty.Optional[ty.Type[BaseModel]] = None,
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
            elif isinstance(params, BaseModel):
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
            elif isinstance(data, BaseModel):
                content = data.json()
        req = self._sync_client.build_request(
            method, url, headers=headers, params=params, content=content
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
                raise sdk_error(detail=str(detail))
            elif status == 401:
                raise errors.AuthError(detail=str(detail))
            else:
                raise e

    def _convert_response_to_model(
        self, data: ty.Any, return_model: ty.Type[BaseModel]
    ) -> ty.Union[None, BaseModel, ty.Page[BaseModel]]:
        """Convert the JSON response to the correct Pydantic model"""
        if data is None:
            return data
        return return_model.parse_obj(data)


_Creating = ty.TypeVar("_Creating", bound=BaseModel)
_Reading = ty.TypeVar("_Reading", bound=BaseModel)
_Updating = ty.TypeVar("_Updating", bound=BaseModel)
_Deleting = ty.TypeVar("_Deleting", bound=BaseModel)
_Returning = ty.TypeVar("_Returning", bound=BaseModel)
_Detail = ty.TypeVar("_Detail", bound=BaseModel)


class ModelClient(
    BaseClient,
    ty.Generic[_Creating, _Reading, _Updating, _Deleting, _Returning, _Detail],
):
    Creating: ty.Type[_Creating]
    Reading: ty.Type[_Reading]
    Updating: ty.Type[_Updating]
    Deleting: ty.Type[_Deleting]
    Returning: ty.Type[_Returning]
    Detail: ty.Type[_Detail]

    def __init__(
        self, sync_client: httpx.Client, async_client: httpx.AsyncClient, path: str
    ) -> None:
        super().__init__(sync_client, async_client, path)
        self.plural_path = f"{self.path}s"

    # TODO: Eventually the `create`, `read`, `update` routes should all
    # have _Detail models and they won't return Union[_Returning, _Detail] but
    # explicitly return `_Detail`. This is temporary until the PAM API is finalized
    def create(
        self, data: ty.Optional[_Creating] = None, **kwargs: ty.Any
    ) -> ty.Union[_Returning, _Detail]:
        data = data if data else self.Creating(**kwargs)
        has_detail, return_model = self._has_detail()
        # Using a type ignore here because the 'detail' stuff is messy and needs to be
        # refactored anyway
        res = self.request(
            "POST", endpoint="create", data=data, return_model=return_model  # type: ignore
        )
        return ty.cast(_Detail, res) if has_detail else ty.cast(_Returning, res)

    async def create_async(
        self, data: ty.Optional[_Creating] = None, **kwargs: ty.Any
    ) -> ty.Union[_Returning, _Detail]:
        data = data if data else self.Creating(**kwargs)
        has_detail, return_model = self._has_detail()
        res = await self.request_async(
            "POST", endpoint="create", data=data, return_model=return_model  # type: ignore
        )
        return ty.cast(_Detail, res) if has_detail else ty.cast(_Returning, res)

    def read(
        self, query: ty.Optional[_Reading] = None, **kwargs: ty.Any
    ) -> ty.Union[_Returning, _Detail]:
        params = query if query else self.Reading(**kwargs)
        has_detail, return_model = self._has_detail()
        res = self.request("GET", params=params, return_model=return_model)  # type: ignore
        return ty.cast(_Detail, res) if has_detail else ty.cast(_Returning, res)

    async def read_async(
        self, query: ty.Optional[_Reading] = None, **kwargs: ty.Any
    ) -> ty.Union[_Returning, _Detail]:
        params = query if query else self.Reading(**kwargs)
        has_detail, return_model = self._has_detail()
        res = await self.request_async("GET", params=params, return_model=return_model)  # type: ignore
        return ty.cast(_Detail, res) if has_detail else ty.cast(_Returning, res)

    def exists(
        self, query: ty.Optional[_Reading] = None, **kwargs: ty.Any
    ) -> ty.Optional[ty.Union[_Returning, _Detail]]:
        params = query if query else self.Reading(**kwargs)
        has_detail, return_model = self._has_detail()
        try:
            res = self.request("GET", params=params, return_model=return_model)  # type: ignore
        except errors.NotFound:
            res = None
        return (
            ty.cast(ty.Optional[_Detail], res)
            if has_detail
            else ty.cast(ty.Optional[_Returning], res)
        )

    async def exists_async(
        self, query: ty.Optional[_Reading] = None, **kwargs: ty.Any
    ) -> ty.Optional[ty.Union[_Returning, _Detail]]:
        params = query if query else self.Reading(**kwargs)
        has_detail, return_model = self._has_detail()
        try:
            res = await self.request_async(
                "GET", params=params, return_model=return_model  # type: ignore
            )
        except errors.NotFound:
            res = None
        return (
            ty.cast(ty.Optional[_Detail], res)
            if has_detail
            else ty.cast(ty.Optional[_Returning], res)
        )

    def update(
        self, data: ty.Optional[_Updating] = None, **kwargs: ty.Any
    ) -> _Returning:
        data = data if data else self.Updating(**kwargs)
        has_detail, return_model = self._has_detail()
        res = self.request(
            "POST",
            endpoint="update",
            data=data,
            return_model=return_model,  # type: ignore
        )
        return res  # type: ignore

    async def update_async(
        self, data: ty.Optional[_Updating] = None, **kwargs: ty.Any
    ) -> _Returning:
        data = data if data else self.Updating(**kwargs)
        has_detail, return_model = self._has_detail()
        res = await self.request_async(
            "POST",
            endpoint="update",
            data=data,
            return_model=return_model,  # type: ignore
        )
        return res  # type: ignore

    def delete(self, **kwargs: ty.Any) -> None:
        self.request("POST", endpoint="delete", data=kwargs, body_model=self.Deleting)

    async def delete_async(self, **kwargs: ty.Any) -> None:
        await self.request_async(
            "POST", endpoint="delete", data=kwargs, body_model=self.Deleting
        )

    def all(
        self,
        query: ty.Optional[_Reading] = None,
        *,
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
        **kwargs: ty.Any,
    ) -> ty.Page[_Returning]:
        params = query if query else self.Reading(**kwargs)
        res = self.request(
            "GET",
            endpoint=self.plural_path,
            params=params,
            page=page,
            size=size,
            return_model=ty.Page[self.Returning],  # type: ignore
        )
        return ty.cast(ty.Page[_Returning], res)

    async def all_async(
        self,
        query: ty.Optional[_Reading] = None,
        *,
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
        **kwargs: ty.Any,
    ) -> ty.Page[_Returning]:
        params = query if query else self.Reading(**kwargs)
        res = await self.request_async(
            "GET",
            endpoint=self.plural_path,
            params=params,
            page=page,
            size=size,
            return_model=ty.Page[self.Returning],  # type: ignore
        )
        return ty.cast(ty.Page[_Returning], res)

    def all_readable(
        self,
        query: ty.Optional[_Reading] = None,
        **kwargs: ty.Any,
    ) -> ty.Page[_Returning]:
        params = query if query else self.Reading(**kwargs)
        res = self.request(
            "GET",
            endpoint=self.plural_path,
            params=params,
            return_model=ty.Page[self.Returning],  # type: ignore
        )
        return ty.cast(ty.Page[_Returning], res)

    async def all_readable_async(
        self,
        query: ty.Optional[_Reading] = None,
        **kwargs: ty.Any,
    ) -> ty.Page[_Returning]:
        params = query if query else self.Reading(**kwargs)
        res = await self.request_async(
            "GET",
            endpoint=self.plural_path,
            params=params,
            return_model=ty.Page[self.Returning],  # type: ignore
        )
        return ty.cast(ty.Page[_Returning], res)

    def _raise_and_handle_errors(self, response: httpx.Response) -> None:
        """Translate errors by status. This allows SDK consumers to get the original
        error from Prodigy Teams, not just the status.
        Does nothing if the reponse was successful
        """
        prefix = self.__class__.__name__
        try:
            super()._raise_and_handle_errors(response)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            error_type = None
            sdk_error = None
            try:
                error_data = e.response.json()
            except json.JSONDecodeError:
                error_data = {}
            detail = error_data.get("detail")
            if detail and isinstance(detail, dict):
                error_type = detail.get("type")
            if error_type:
                sdk_error = getattr(errors, error_type, None)
            if sdk_error:
                raise sdk_error(detail=str(detail))
            elif status == 400:
                raise getattr(errors, f"{prefix}Invalid", errors.Invalid)
            elif status == 403:
                raise getattr(errors, f"{prefix}Forbidden", errors.Forbidden)
            elif status == 404:
                raise getattr(errors, f"{prefix}NotFound", errors.NotFound)
            else:
                raise e

    def _has_detail(self) -> ty.Tuple[bool, ty.Union[_Returning, _Detail]]:
        if hasattr(self, "Detail"):
            return True, ty.cast(_Detail, self.Detail)
        else:
            return False, ty.cast(_Detail, self.Returning)


_ReadingLatest = ty.TypeVar("_ReadingLatest", bound=BaseModel)
_ListingLatest = ty.TypeVar("_ListingLatest", bound=BaseModel)


class VersionedModelClient(
    ModelClient,
    ty.Generic[
        _Creating,
        _Reading,
        _Updating,
        _Deleting,
        _Returning,
        _Detail,
        _ReadingLatest,
        _ListingLatest,
    ],
):
    Creating: ty.Type[_Creating]
    Reading: ty.Type[_Reading]
    Updating: ty.Type[_Updating]
    Deleting: ty.Type[_Deleting]
    Returning: ty.Type[_Returning]
    Detail: ty.Type[_Detail]
    ReadingLatest: ty.Type[_ReadingLatest]
    ListingLatest: ty.Type[_ListingLatest]

    def all_latest(self, *, body: _ListingLatest) -> ty.Page[_Returning]:
        res = self.request(
            "POST",
            endpoint="all-latest",
            data=body,
            return_model=ty.Page[self.Returning],  # type: ignore
        )
        return ty.cast(ty.Page[_Returning], res)

    async def all_latest_async(self, *, body: _ListingLatest) -> ty.Page[_Returning]:
        res = await self.request_async(
            "POST",
            endpoint="all-latest",
            data=body,
            return_model=ty.Page[self.Returning],  # type: ignore
        )
        return ty.cast(ty.Page[_Returning], res)  # type: ignore

    def latest(self, *, body: _ReadingLatest) -> _Returning:
        res = self.request(
            "POST",
            endpoint="latest",
            data=body,
            return_model=self.Detail,
        )
        return ty.cast(_Returning, res)

    async def latest_async(self, *, body: _ReadingLatest) -> _Returning:
        res = await self.request_async(
            "POST",
            endpoint="latest",
            data=body,
            return_model=self.Detail,
        )
        return ty.cast(_Returning, res)
