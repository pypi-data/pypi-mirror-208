from typing import Any, Callable
import aiohttp
import ujson


class Request:
    __base: Callable[..., str] | str = None

    @property
    async def baseurl(self) -> str | None:
        if isinstance(self.__base, str):
            return self.__base
        if self.__base.__class__.__name__ == 'function':
            url = self.__base()
            if url.__class__.__name__ == 'coroutine':
                return await url
            return url

    @baseurl.setter
    def baseurl(self, base_url: Callable[..., str] | str):
        self.__base = base_url

    async def __call__(self, method: str, url: str, **kwargs) -> Any:
        # convert params values to str
        if params := kwargs['params']:
            for key, value in params.items():
                kwargs['params'][key] = str(value)
        # assure that `method` supports
        assert (method := method.lower()) in ('get', 'post', 'put', 'delete')
        # request
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with getattr(session, method)(
                    await self.__url(url, kwargs['nobase']),
                    json=kwargs['body'],
                    params=kwargs['params'],
                    headers=kwargs['headers'],
                    data=kwargs['data']
            ) as response:
                try:
                    return await response.json()
                except Exception:
                    raise ValueError(await response.text())

    async def get(
            self,
            url: str,
            *,
            params: dict[str, Any] = None,
            headers: dict[str, Any] = None,
            body: dict[str, Any] = None,
            data: dict[str, Any] = None,
            nobase: bool = False
    ) -> Any:
        return await self('get', url, params=params, headers=headers, body=body, data=data, nobase=nobase)

    async def post(
            self,
            url: str,
            *,
            params: dict[str, Any] = None,
            headers: dict[str, Any] = None,
            body: dict[str, Any] = None,
            data: dict[str, Any] = None,
            nobase: bool = False
    ) -> Any:
        return await self('post', url, params=params, headers=headers, body=body, data=data, nobase=nobase)

    async def put(
            self,
            url: str,
            *,
            params: dict[str, Any] = None,
            headers: dict[str, Any] = None,
            body: dict[str, Any] = None,
            data: dict[str, Any] = None,
            nobase: bool = False
    ) -> Any:
        return await self('put', url, params=params, headers=headers, body=body, data=data, nobase=nobase)

    async def delete(
            self,
            url: str,
            *,
            params: dict[str, Any] = None,
            headers: dict[str, Any] = None,
            body: dict[str, Any] = None,
            data: dict[str, Any] = None,
            nobase: bool = False
    ) -> Any:
        return await self('delete', url, params=params, headers=headers, body=body, data=data, nobase=nobase)

    async def __url(self, url: str, nobase: bool = False):
        if not (base := await self.baseurl) or nobase:
            return url
        if base.endswith('/') and url.startswith('/'):
            return base[:-1] + url
        elif base.endswith('/') and not url.startswith('/'):
            return base + url
        elif not base.endswith('/') and url.startswith('/'):
            return base + url
        elif not base.endswith('/') and not url.startswith('/'):
            return f'{base}/{url}'


request = Request()
